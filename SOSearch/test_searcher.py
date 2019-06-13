# encoding: utf-8

import math
import operator
from nltk.corpus import stopwords
import sqlite3
import configparser
import string


class SearchEngine:
    stop_words = set()

    config_path = ''
    config_encoding = ''
    config = ''
    K1 = 0
    B = 0
    N = 0
    AVG_L = 0

    conn = None

    def __init__(self, config_path, config_encoding):
        self.config_path = config_path
        self.config_encoding = config_encoding
        self.config = configparser.ConfigParser()
        self.config.read(config_path, config_encoding)
        self.stop_words = stopwords.words('english') + list(string.punctuation)
        self.conn = sqlite3.connect(self.config['DEFAULT']['db_path'])

        self.K1 = float(self.config['DEFAULT']['k1'])
        self.B = float(self.config['DEFAULT']['b'])
        self.N = int(self.config['DEFAULT']['n'])
        self.AVG_L = float(self.config['DEFAULT']['avg_l'])

    def __del__(self):
        self.conn.close()

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def clean_list(self, seg_list):
        cleaned_dict = {}
        n = 0
        for i in seg_list:
            i = i.strip().lower()
            if i != '' and not self.is_number(i) and i not in self.stop_words:
                n = n + 1
                if i in cleaned_dict:
                    cleaned_dict[i] = cleaned_dict[i] + 1
                else:
                    cleaned_dict[i] = 1
        return n, cleaned_dict

    def fetch_from_question_db(self, term):
        c = self.conn.cursor()
        c.execute('SELECT * FROM question_index where term=?', (term,))
        return c.fetchone()

    def fetch_from_answer_db(self, term):
        c = self.conn.cursor()
        c.execute('SELECT * FROM answer_index where term=?', (term,))
        return c.fetchone()

    def fetch_from_tag_db(self, tag):
        c = self.conn.cursor()
        c.execute('SELECT * FROM tag_index WHERE tag=?', (tag,))
        return c.fetchone()

    def result_by_BM25(self, sentence, model_name):

        seg_list = sentence.split()

        n, cleaned_dict = self.clean_list(seg_list)
        BM25_scores = {}

        if (str(model_name) == 'tag'):
            results = []
            for term in cleaned_dict.keys():
                r = self.fetch_from_tag_db(term)
                if r is None:
                    continue
                docs = r[2].split('\n')
                for doc in docs:
                    result_list = [doc.split('\t')[0], [1] + doc.split('\t')[3:]]
                    if len(result_list[1]) > 1:             # convert vote from string to int
                        result_list[1][1] = int(result_list[1][1])
                    results.append(result_list)
            if len(results) == 0:
                return 0, []
            else:
                return 1, results

        for term in cleaned_dict.keys():
            if(str(model_name) == '<class \'websearch.models.Answer\'>'):
                self.K1 = float(self.config['ANSWER']['k1'])
                self.B = float(self.config['ANSWER']['b'])
                self.N = int(self.config['ANSWER']['n'])
                self.AVG_L = float(self.config['ANSWER']['avg_l'])
                r = self.fetch_from_answer_db(term)
            else:
                r = self.fetch_from_question_db(term)
                self.K1 = float(self.config['QUESTION']['k1'])
                self.B = float(self.config['QUESTION']['b'])
                self.N = int(self.config['QUESTION']['n'])
                self.AVG_L = float(self.config['QUESTION']['avg_l'])
            if r is None:
                continue
            df = r[1]
            w = math.log2((self.N - df + 0.5) / (df + 0.5))
            docs = r[2].split('\n')
            for doc in docs:
                docid, tf, ld, *extra_fields = doc.split('\t')
                tf = int(tf)
                ld = int(ld)
                s = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
                if docid in BM25_scores:
                    BM25_scores[docid][0] = BM25_scores[docid][0] + s
                else:
                    result_list = [s, *extra_fields]
                    if len(result_list) > 1:  # convert vote from string to int
                        result_list[1] = int(result_list[1])
                    BM25_scores[docid] = result_list
        # BM25_scores = sorted(BM25_scores.items(), key=operator.itemgetter(1))
        BM25_scores = sorted(BM25_scores.items(), key=lambda x: x[1][0])
        BM25_scores.reverse()
        if len(BM25_scores) == 0:
            return 0, []
        else:
            return 1, BM25_scores

    def search(self, sentence, model_name):
        return self.result_by_BM25(sentence, model_name)


if __name__ == "__main__":
    se = SearchEngine('config.txt', 'utf-8')
    flag, rs = se.search('python result', '<class \'websearch.models.Answer\'>')
    print(rs[:10], len(rs))
