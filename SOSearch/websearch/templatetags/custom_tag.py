from django import template
from django.utils.html import format_html
import urllib.parse

register = template.Library()


def build_prefix(query="", form="", sort_by="", dropdown=None):
    prefix = ""
    if query:
        prefix += "q={}&amp;".format(urllib.parse.quote(query))
    if form:
        for model_name in form.cleaned_data['models']:
            prefix += "models={}&amp;".format(model_name)
    if dropdown:
        if dropdown == 1:
            prefix += "models=websearch.question&amp;model=websearch.answer&amp;"
        elif dropdown == 2:
            prefix += "models=websearch.question&amp;"
        elif dropdown == 3:
            prefix += "models=websearch.answer&amp;"
    if sort_by:
        prefix += "sort_by={}&amp;".format(sort_by)
    return prefix


@register.simple_tag
def prev_or_next_page(page_type, page_num, query="", form="", sort_by=""):
    prefix = build_prefix(query, form, sort_by)
    if page_type == 'prev':
        page_ele = '''<li><a href="?{}page={}"><span aria-hidden="true">&laquo;</span></a></li>'''.format(
            prefix, page_num)
        return format_html(page_ele)
    elif page_type == 'next':
        page_ele = '''<li><a href="?{}page={}"><span aria-hidden="true">&raquo;</span></a></li>'''.format(
            prefix, page_num)
        return format_html(page_ele)
    else:
        return ''


@register.simple_tag
def circle_page(current_page, loop_num, query="", form="", sort_by=""):
    prefix = build_prefix(query, form, sort_by)
    offset = abs(current_page - loop_num)
    if offset < 3:
        if current_page == loop_num:
            page_ele = '''<li class="active"><a href="?{}page={}">{}</a></li>'''.format(prefix, loop_num, loop_num)
        else:
            page_ele = '''<li class=""><a href="?{}page={}">{}</a></li>'''.format(prefix, loop_num, loop_num)
        return format_html(page_ele)
    else:
        return ''


@register.simple_tag
def build_sort_by_link(show_name="", query="", form="", sort_by=""):
    prefix = build_prefix(query, form, sort_by)
    if prefix.endswith("&amp;"):
        prefix = prefix[:-5]
    if show_name:
        html_ele = '''<a href="?{}">{}</a>'''.format(prefix, show_name)
    else:
        html_ele = '''<a href="?{}">{}</a>'''.format(prefix, sort_by)
    return format_html(html_ele)


@register.simple_tag
def build_dropdown_link(type, show_name, query="", form="", sort_by=""):
    prefix = build_prefix(query, form, sort_by)
    if type == 1:
        prefix += "models=websearch.question&amp;models=websearch.answer"
    elif type == 2:
        prefix += "models=websearch.question"
    elif type == 3:
        prefix += "models=websearch.answer"
    html_ele = '''<a href="?{}">{}</a>'''.format(prefix, show_name)
    return format_html(html_ele)
