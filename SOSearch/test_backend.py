# encoding: utf-8
"""
A very basic, ORM-based backend for simple search during tests.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from warnings import warn

from django.conf import settings
from django.db.models import Q
from django.utils import six

from haystack import connections
from haystack.backends import BaseEngine, BaseSearchBackend, BaseSearchQuery, log_query, SearchNode
from haystack.inputs import PythonData
from haystack.models import SearchResult
from haystack.utils import get_model_ct_tuple

from test_searcher import SearchEngine
from test_indexer import IndexModule
import sqlite3
import os

if settings.DEBUG:
    import logging


    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger = logging.getLogger('haystack.simple_backend')
    logger.setLevel(logging.WARNING)
    logger.addHandler(NullHandler())
    logger.addHandler(ch)
else:
    logger = None


class TestSearchBackend(BaseSearchBackend):
    def __init__(self, connection_alias, **connection_options):
        super(TestSearchBackend, self).__init__(connection_alias, **connection_options)
        self.extra_field_keys = list(connections[self.connection_alias].get_unified_index().all_searchfields().keys())
        try:
            self.extra_field_keys.remove('text')
        except Exception as e:
            pass

    def update(self, indexer, iterable, commit=True):
        table_name = indexer.get_model().__name__.lower() + '_index'
        index_module = IndexModule(table_name, 'test_db.sqlite3')
        docs = []
        for obj in iterable:
            docs.append(indexer.full_prepare(obj))
            if table_name == 'question_index':
                docs[-1]['tags'] = obj.tags
        index_module.update(docs, self.extra_field_keys)
        print('index contains {} docs, average length: {}'.format(index_module.count, index_module.avg_dl))

    def remove(self, obj, commit=True):
        warn('remove is not implemented in this backend')

    def clear(self, models=None, commit=True):
        conn = sqlite3.connect('test_db.sqlite3')
        c = conn.cursor()

        c.execute('''DROP TABLE IF EXISTS question_index''')
        c.execute('''CREATE TABLE question_index
                     (term TEXT PRIMARY KEY, df INTEGER, docs TEXT)''')
        c.execute('''DROP TABLE IF EXISTS answer_index''')
        c.execute('''CREATE TABLE answer_index
                     (term TEXT PRIMARY KEY, df INTEGER, docs TEXT)''')
        c.execute('''DROP TABLE IF EXISTS tag_index''')
        c.execute('''CREATE TABLE tag_index
                             (tag TEXT PRIMARY KEY, df INTEGER, docs TEXT)''')
        conn.commit()
        conn.close()

        if os.path.exists('question_index'):
            os.remove('question_index')
        if os.path.exists('answer_index'):
            os.remove('answer_index')
        # if os.path.exists('Question_index.txt'):
        #     os.remove('Question_index.txt')
        # if os.path.exists('Answer_index.txt'):
        #     os.remove('Answer_index.txt')
        # warn('clear is not implemented in this backend')

    @log_query
    def search(self, query_string, sort_by=None, start_offset=None, end_offset=None, **kwargs):
        hits = 0
        results = []
        result_class = SearchResult
        models = connections[self.connection_alias].get_unified_index().get_indexed_models()

        SE = SearchEngine('config.txt', 'utf-8')

        if kwargs.get('result_class'):
            result_class = kwargs['result_class']

        if kwargs.get('models'):
            models = kwargs['models']

        search_hits = 0
        search_res = []

        if query_string:
            form_str = query_string.strip()
            if (form_str[0] == '[' and form_str[-1] == ']'):
                model = 'tag'
                flag, rs = SE.search(query_string[1:-1], model)
                search_hits += len(rs)
                search_res += rs
            else:
                for model in models:
                    flag, rs = SE.search(query_string, model)
                    search_hits += len(rs)
                    search_res += rs

        def takeSecond(elem):
            return elem[1]

        search_res = sorted(search_res, key=takeSecond, reverse=True)
        if sort_by:
            sort_by_key = sort_by[0]
            reverse_flag = False
            if sort_by_key.startswith('-'):
                reverse_flag = True
                sort_by_key = sort_by_key[1:]
            if sort_by_key in self.extra_field_keys:
                sort_by_idx = self.extra_field_keys.index(sort_by_key)
                if search_res and len(search_res[0][1]) > sort_by_idx + 1:
                    search_res = sorted(search_res, key=lambda x: x[1][sort_by_idx + 1], reverse=reverse_flag)

        if start_offset is not None:
            if end_offset is not None:
                search_res = search_res[start_offset:end_offset]
            else:
                search_res = search_res[start_offset:]

        for match in search_res:
            # match.__dict__.pop('score', None)
            app_label, model_name, searched_id = match[0].split('.')
            # print(app_label, model_name, searched_id, match[1])
            result = result_class(app_label, model_name, searched_id, 0)
            # For efficiency.
            # result._model = match.__class__
            # result._object = match
            results.append(result)

        return {
            'results': results,
            'hits': search_hits,
        }

    def prep_value(self, db_field, value):
        return value

    def more_like_this(self, model_instance, additional_query_string=None,
                       start_offset=0, end_offset=None,
                       limit_to_registered_models=None, result_class=None, **kwargs):
        return {
            'results': [],
            'hits': 0
        }


class TestSearchQuery(BaseSearchQuery):
    def build_query(self):
        if not self.query_filter:
            return '*'

        return self._build_sub_query(self.query_filter)

    def _build_sub_query(self, search_node):
        term_list = []

        for child in search_node.children:
            if isinstance(child, SearchNode):
                term_list.append(self._build_sub_query(child))
            else:
                value = child[1]

                if not hasattr(value, 'input_type_name'):
                    value = PythonData(value)

                term_list.append(value.prepare(self))

        return (' ').join(map(six.text_type, term_list))


class TestEngine(BaseEngine):
    backend = TestSearchBackend
    query = TestSearchQuery
