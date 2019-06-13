import sys
import os
import argparse
import time
import json
import requests

import scrapy
from scrapy.cmdline import execute
from scrapy.utils.request import request_fingerprint
import scrapy.downloadermiddlewares.httpproxy
import scrapy.downloadermiddlewares.retry
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from items import Question, Answer, QuestionAnswers, User, Comment, LinkedQuestion, RelatedQuestion
import utils as F


class StackOverflowQuestionAnswerSpider(scrapy.Spider):
    name = 'StackOverflow_QA'
    base_url = 'https://stackoverflow.com'
    # handle_httpstatus_list = [429]
    custom_settings = {
        # 'RETRY_TIMES': 20,
        # 'RETRY_HTTP_CODES': [429, 500, 502, 503, 504, 400, 408],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'middlewares.RandomUserAgentMiddleware': 501,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # 'middlewares.TooManyRequestsRetryMiddleware': 551,
            'middlewares.ChangeProxyRetryMiddleware': 552
        },
        'METAREFRESH_ENABLED': False,
        'DOWNLOAD_DELAY': 0.25,
        'AUTOTHROTTLE_ENABLED': True
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_number = int(getattr(self, 'start', 0))
        self.item_limit = int(getattr(self, 'limit', 10))
        self.parsed_item_count = 0
        # self.fingerprints = set()

        # prepare question list
        self.question_list_path = getattr(self, 'question_list_path', './data/question_list.json')
        self.question_list = []
        self.parse_question_list()

        # prepare crawled links
        self.crawled_file_path = getattr(self, 'crawled_file_path', './data/crawled_question_answer.json')
        self.crawled_links = set()
        self.parse_crawled_links()

        # prepare proxies
        self.direct_connection = getattr(self, 'direct_connection', False)
        self.parse_direct_connection()
        self.proxy_number = int(getattr(self, 'proxy_number', 1))
        self.proxy_addr_list = []
        if not self.direct_connection:
            self.fetch_proxy_addr(num=self.proxy_number)

    def parse_direct_connection(self):
        if isinstance(self.direct_connection, str):
            if self.direct_connection.lower() == 'true':
                self.direct_connection = True
            else:
                self.direct_connection = False

    def parse_question_list(self):
        if os.path.exists(self.question_list_path):
            self.logger.info('Loading question list from {}...'.format(self.question_list_path))
            self.question_list = json.load(open(self.question_list_path, 'r'))
            self.logger.info('Load process done!')
        else:
            raise FileNotFoundError('Cannot find file {}!'.format(self.question_list_path))

    def parse_crawled_links(self):
        st = int(self.item_number / 10000)
        ed = int(self.item_limit / 10000)
        if st > 0 and ed > 0:
            specific_crawled_file_path = self.crawled_file_path.split('.json')
            specific_crawled_file_path = '{}_{}w_{}w.json'.format(specific_crawled_file_path[0], str(st), str(ed))
            self.crawled_file_path = specific_crawled_file_path
        if os.path.exists(self.crawled_file_path):
            self.logger.info('Loading crawled links from {}...'.format(self.crawled_file_path))
            try:
                self.crawled_links = set(json.load(open(self.crawled_file_path, 'r')))
            except Exception as e:
                self.logger.error(e)
            self.logger.info('Load process done!')

    def save_crawled_links(self):
        self.logger.info('Dumping crawled links to {}...'.format(self.crawled_file_path))
        json.dump(list(self.crawled_links), open(self.crawled_file_path, 'w'))
        self.logger.info('Dumping process done!')

    def get_timestamp(self):
        return int(time.time()*1000)

    # def request_fingerprint(self, request):
    #     return request_fingerprint(request)

    def get_next_url(self):
        url = None
        while self.base_url + self.question_list[self.item_number]['link'] in self.crawled_links and self.item_number \
                <= self.item_limit:
            self.item_number += 1
        if self.item_number <= self.item_limit:
            url = self.base_url + self.question_list[self.item_number]['link']
            self.item_number += 1
        return url

    def get_next_all_comments_url(self, next_request_id):
        url = 'https://stackoverflow.com/posts/{}/comments?_={}'.format(next_request_id, self.get_timestamp())
        return url

    def start_requests(self):
        # yield scrapy.Request('https://stackoverflow.com/questions/54531254/python-raising-errors-within-list'
        #                      '-comprehension-or-a-better-alternative/', callback=self.parse,
        #                      errback=self.process_exception)
        while self.item_number <= self.item_limit:
            next_url = self.get_next_url()
            if next_url:
                request = scrapy.Request(next_url, callback=self.parse, errback=self.process_exception,
                                     dont_filter=True)
                if not self.direct_connection:
                    request.meta['proxy'] = self.get_proxy()
                # request.meta['dont_retry'] = True
                yield request

    def remove_invalid_proxy(self, proxy):
        proxy_addr = proxy.split('//')[-1]
        try:
            self.proxy_addr_list.remove(proxy_addr)
        except Exception as e:
            pass
            # self.logger.error(e)

    def get_proxy(self, username='alexzhangfm@126.com', password='WSM19proxy'):
        proxy_addr = F.rand_item(self.proxy_addr_list)
        proxy = 'http://{}:{}@{}'.format(username, password, proxy_addr)
        return proxy

    def fetch_proxy_addr(self, num=10, app_key='aedb69fe180a5a3f3dec25858f09aed9'):
        req_url = 'http://api.qingtingip.com/ip?app_key={}&num={}&ptc=https&fmt=text&lb=\n&port=0&mr=1&'.format(
            app_key, num)
        result = requests.get(req_url).text
        result_list = result.split('\n')
        self.proxy_addr_list.extend(result_list)

    def change_request_proxy(self, request):
        # change proxy
        invalid_proxy = request.meta['proxy']
        self.logger.info('Removing invalid proxy: {}'.format(invalid_proxy))
        self.remove_invalid_proxy(invalid_proxy)
        if len(self.proxy_addr_list) < self.proxy_number:
            fetch_num = self.proxy_number - len(self.proxy_addr_list)
            self.fetch_proxy_addr(num=fetch_num)
        new_proxy = self.get_proxy()
        self.logger.info('Retrying request with new proxy: {}'.format(new_proxy))
        request.meta['proxy'] = new_proxy
        return request

    def process_exception(self, failure):
        if failure.check(HttpError):
            request = failure.request
            self.logger.error('HttpError ({}) on {}'.format(failure.value.response.status, request.url))
            if failure.value.response.status == 429:
                if not self.direct_connection:
                    modified_request = self.change_request_proxy(request)
                    yield modified_request
                else:
                    sleep_time = F.rand_int((180, 600))
                    self.logger.info('Meet 429 code! Sleep for {} seconds...'.format(sleep_time))
                    self.crawler.engine.pause()
                    time.sleep(sleep_time)
                    self.logger.info('Wake up!')
                    self.crawler.engine.unpause()
                    yield request
        else:
            self.logger.error('{} on {}'.format(repr(failure), failure.request.url))
        # elif failure.check(TimeoutError, TCPTimedOutError):
        #     request = failure.request
        #     self.logger.error('TimeoutError on %s', request.url)
        #     if not self.direct_connection:
        #         # change proxy
        #         invalid_proxy = request.meta['proxy']
        #         self.logger.info('Remove proxy {}'.format(invalid_proxy))
        #         self.remove_invalid_proxy(invalid_proxy)
        #         if len(self.proxy_addr_list) < self.proxy_number:
        #             fetch_num = self.proxy_number - len(self.proxy_addr_list)
        #             self.fetch_proxy_addr(num=fetch_num)
        #         request.meta['proxy'] = self.get_proxy()
        #         yield request
        # else:
        #     self.logger.error(repr(failure))

    def parse(self, response):
        # self.logger.info('Item count: {}, request url: {}'.format(self.item_number, response.url))

        # handle http error(ignore and continue)
        # if response.status in self.handle_httpstatus_list:
        #     # if self.item_number <= self.item_limit:
        #     #     yield response.follow(self.get_next_url(), self.parse, dont_filter=True)
        #     return

        # handle duplicate request(ignore and continue)
        # if self.request_fingerprint(response.request) in self.fingerprints:
        #     self.logger.info('Ignore duplicate request: {}'.format(response.url))
        #     # if self.item_number <= self.item_limit:
        #     #     yield response.follow(self.get_next_url(), self.parse, dont_filter=True)
        #     return
        # else:
        #     self.fingerprints.add(self.request_fingerprint(response.request))

        # handle duplicate request(ignore and continue)
        if response.url in self.crawled_links:
            self.logger.info('Ignore duplicate request: {}'.format(response.url))
            return
        else:
            self.parsed_item_count += 1
            self.crawled_links.add(response.url)
            self.logger.info('Parsed item count: {}, url: {}'.format(self.parsed_item_count, response.url))

        if self.parsed_item_count % 100 == 99:
            self.logger.info('Current proxy addr list: {}'.format(self.proxy_addr_list))
            self.save_crawled_links()

        # question & answers
        pending_request_list = []
        question = self.parse_question(response, pending_request_list)
        answers = self.parse_answers(response, pending_request_list)
        linked_questions = self.parse_linked_questions(response)
        related_questions = self.parse_related_questions(response)
        question_answers = QuestionAnswers()
        question_answers['question'] = question
        question_answers['answers'] = answers
        question_answers['linked_questions'] = linked_questions
        question_answers['related_questions'] = related_questions

        if pending_request_list:
            req = self.prepare_nex_all_comments_request(pending_request_list, question_answers)
            yield req
        else:
            yield question_answers
            return
            # if self.item_number <= self.item_limit:
            #     yield scrapy.Request(self.get_next_url(), self.parse, dont_filter=True)

    def prepare_nex_all_comments_request(self, pending_request_list, question_answers):
        next_request_type = pending_request_list[0][0]
        next_request_id = pending_request_list[0][1]
        pending_request_list.remove(pending_request_list[0])
        next_all_comments_url = self.get_next_all_comments_url(next_request_id)
        req = scrapy.Request(next_all_comments_url, callback=self.parse_all_comments, errback=self.process_exception,
                             dont_filter=True)
        if not self.direct_connection:
            req.meta['proxy'] = self.get_proxy()
        req.meta['question_answers'] = question_answers
        req.meta['pending_request_list'] = pending_request_list
        req.meta['request_type'] = next_request_type
        req.meta['request_id'] = next_request_id
        return req

    def parse_all_comments(self, response):
        question_answers = response.meta['question_answers']
        pending_request_list = response.meta['pending_request_list']
        request_type = response.meta['request_type']
        request_id = response.meta['request_id']
        comments_response = response.css('.comment')
        if request_type == 'question':
            question = question_answers['question']
            question['comments'] = self.parse_comments(comments_response)
            question_answers['question'] = question
        elif request_type == 'answer':
            answers = question_answers['answers']
            for answer in answers:
                if answer['id'] == request_id:
                    answer['comments'] = self.parse_comments(comments_response)
                    break
            question_answers['answers'] = answers
        else:
            raise RuntimeError('Not support type: {}!'.format(request_type))

        if pending_request_list:
            req = self.prepare_nex_all_comments_request(pending_request_list, question_answers)
            yield req
        else:
            yield question_answers
            return
            # if self.item_number <= self.item_limit:
            #     yield scrapy.Request(self.get_next_url(), self.parse, dont_filter=True)

    def parse_question(self, response, pending_request_list):
        # question
        question = Question()
        # question header
        question_header = response.css('#question-header')
        question['title'] = question_header.css('h1 a::text').get()
        question['link'] = question_header.css('h1 a::attr(href)').get()
        # question content
        question_main = response.css('#mainbar #question')
        question['id'] = question_main.css('.js-voting-container::attr(data-post-id)').get()
        question['vote'] = question_main.css('.js-vote-count::text').get()
        question['star'] = question_main.css('.js-favorite-count::text').get()
        question['content'] = question_main.css('.post-text').get()
        question['tags'] = question_main.css('.post-tag::text').getall()
        question['status'] = question_main.css('.question-status').get()
        # question users
        users_response = question_main.css('.post-signature')
        question['users'] = self.parse_users(users_response)
        # question comments
        comments_response = question_main.css('.comment')
        if not question_main.css('.js-show-link.comments-link.dno') and question['id']:
            pending_request_list.append(('question', question['id']))
        question['comments'] = self.parse_comments(comments_response)
        # question status
        question_status = response.css('#sidebar .question-stats tr td:nth-child(2)')
        for idx, question_stat in enumerate(question_status):
            if idx == 0:
                question['asked'] = question_stat.css('p::attr(title)').get()
            elif idx == 1:
                viewed_times = question_stat.css('b::text').get()
                time_idx = viewed_times.find('times')
                viewed_times = viewed_times[:time_idx]
                viewed_times = viewed_times.replace(',', '')
                viewed_times = viewed_times.strip()
                question['viewed'] = viewed_times
            elif idx == 2:
                question['active'] = question_stat.css('.lastactivity-link::attr(title)').get()
            else:
                self.logger.warning('Question status idx: {}, stat: {}'.format(idx, question_stat))
        return question

    def parse_answers(self, response, pending_request_list):
        answers = []
        answers_response = response.css('#mainbar .answer')
        for answer_response in answers_response:
            answer = Answer()
            answer['id'] = answer_response.css('.js-voting-container::attr(data-post-id)').get()
            answer['vote'] = answer_response.css('.js-vote-count::text').get()
            if answer_response.css('.js-accepted-answer-indicator.d-none'):
                answer['accepted'] = False
            else:
                answer['accepted'] = True
            answer['content'] = answer_response.css('.post-text').get()
            answer_users_response = answer_response.css('.post-signature')
            answer['users'] = self.parse_users(answer_users_response)
            answer_comments_response = answer_response.css('.comment')
            if not answer_response.css('.js-show-link.comments-link.dno') and answer['id']:
                pending_request_list.append(('answer', answer['id']))
            answer['comments'] = self.parse_comments(answer_comments_response)
            answers.append(answer)
        return answers

    def parse_users(self, users_response):
        users = []
        for user_response in users_response:
            user = User()
            if user_response.css('.owner'):
                user['is_owner'] = True
                user['action'] = user_response.css('.user-action-time::text').get()
                user['revision'] = None
            else:
                user['is_owner'] = False
                if user_response.css('.user-action-time a'):
                    user['action'] = user_response.css('.user-action-time a::text').get()
                    user['revision'] = user_response.css('.user-action-time a::attr(href)').get()
                else:
                    user['action'] = user_response.css('.user-action-time::text').get()
                    user['revision'] = None
            if user['action']:
                user['action'] = user['action'].strip()
            user['time'] = user_response.css('.relativetime::attr(title)').get()
            user['name'] = user_response.css('.user-details span::text').get()
            if not user['name']:
                user['name'] = user_response.css('.user-details a::text').get()
            user['link'] = user_response.css('.user-details a::attr(href)').get()
            user['reputation'] = user_response.css('.user-details .-flair .reputation-score::text').get()
            if user['reputation']:
                user['reputation'].replace(',', '').strip()
            user['gold'] = user_response.css('.user-details .-flair .badge1 + .badgecount::text').get()
            if user['gold']:
                user['gold'].replace(',', '').strip()
            user['silver'] = user_response.css('.user-details .-flair .badge2 + .badgecount::text').get()
            if user['silver']:
                user['silver'].replace(',', '').strip()
            user['bronze'] = user_response.css('.user-details .-flair .badge3 + .badgecount::text').get()
            if user['bronze']:
                user['bronze'].replace(',', '').strip()
            users.append(user)
        return users

    def parse_comments(self, comments_response):
        comments = []
        for comment_response in comments_response:
            comment = Comment()
            comment['score'] = comment_response.css('.comment-score span::text').get()
            comment['content'] = comment_response.css('.comment-copy').get()
            comment['user'] = comment_response.css('.comment-user::text').get()
            comment['user_href'] = comment_response.css('.comment-user::attr(href)').get()
            comment['date'] = comment_response.css('.comment-date .relativetime-clean::attr(title)').get()
            comments.append(comment)
        return comments

    def parse_linked_questions(self, response):
        linked_questions = []
        linked_questions_response = response.css('#sidebar .sidebar-linked .linked .spacer')
        for linked_question_response in linked_questions_response:
            if not linked_question_response.css('.more'):
                linked_question = LinkedQuestion()
                linked_question['accepted'] = False
                if linked_question_response.css('.answered-accepted'):
                    linked_question['accepted'] = True
                linked_question['vote'] = linked_question_response.css('.answer-votes::text').get()
                linked_question['title'] = linked_question_response.css('.question-hyperlink::text').get()
                linked_question['link'] = linked_question_response.css('.question-hyperlink::attr(href)').get()
                start_idx = linked_question['link'].find('/', linked_question['link'].find('questions'))
                end_idx = linked_question['link'].find('/', start_idx + 1)
                linked_question['id'] = linked_question['link'][start_idx+1:end_idx]
                linked_questions.append(linked_question)
        return linked_questions

    def parse_related_questions(self, response):
        related_questions = []
        related_questions_response = response.css('#sidebar .sidebar-related .related .spacer')
        for related_question_response in related_questions_response:
            related_question = RelatedQuestion()
            related_question['accepted'] = False
            if related_question_response.css('.answered-accepted'):
                related_question['accepted'] = True
            related_question['vote'] = related_question_response.css('.answer-votes::text').get()
            related_question['title'] = related_question_response.css('.question-hyperlink::text').get()
            related_question['link'] = related_question_response.css('.question-hyperlink::attr(href)').get()
            start_idx = related_question['link'].find('/', related_question['link'].find('questions'))
            end_idx = related_question['link'].find('/', start_idx + 1)
            related_question['id'] = related_question['link'][start_idx + 1:end_idx]
            related_questions.append(related_question)
        return related_questions


def initArgParser():
    parser = argparse.ArgumentParser(description='StackOverflow Spider')
    parser.add_argument('--o', type=str, default='question_answer_spider', help='output file name')
    parser.add_argument('--l', type=str, default=str(100), help='item limit')
    parser.add_argument('--s', type=str, default=str(0), help='start item number')
    parser.add_argument('--p', type=str, default='./data/', help='data path')
    parser.add_argument('--dc', action='store_true', default=False, help='direct connection(do not use proxy')
    parser.add_argument('--pn', type=str, default=str(1), help='proxy number')
    args = parser.parse_args()
    return args

def main():
    args = initArgParser()
    item_limit = args.l
    start_item_number = args.s
    direct_connection = str(args.dc)
    proxy_number = args.pn
    output_file_full_name = args.p + args.o + time.strftime('_%y%m%d_%H%M%S') + '.json'

    execute(['scarpy', 'runspider', 'question_answer_spider.py', '-a', 'limit=' + item_limit,
             '-a', 'start=' + start_item_number, '-a', 'direct_connection=' + direct_connection, '-a',
             'proxy_number=' + proxy_number,
             '-o',
             output_file_full_name])

    return

if __name__ == '__main__':
    main()
