import sys
import os
import argparse
import time

import scrapy
from scrapy.cmdline import execute


class StackOverflowQuestionListSpider(scrapy.Spider):
    name = 'StackOverflow_QL'
    base_url = 'https://stackoverflow.com/questions?sort=newest&pagesize=50&page='
    custom_settings = {
        'RETRY_TIMES': 20,
        'RETRY_HTTP_CODES': [429, 500, 502, 503, 504, 400, 408],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'middlewares.RandomUserAgentMiddlware': 501,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'middlewares.TooManyRequestsRetryMiddleware': 551,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_limit = int(getattr(self, 'limit', 5))
        self.page_number = int(getattr(self, 'start', 1))

    def get_next_url(self):
        url = self.base_url + str(self.page_number)
        self.page_number += 1
        return url

    def start_requests(self):
        yield scrapy.Request(self.get_next_url(), self.parse)

    def parse(self, response):
        for question_list in response.css('div.question-summary'):
            question = question_list.css('div.summary')
            yield {
                'link': question.css('h3 a::attr(href)').get(),
                'time': question.css('div.started div.user-action-time span::attr(title)').get(),
            }
        if self.page_number <= self.page_limit:
            yield response.follow(self.get_next_url(), self.parse)

def initArgParser():
    parser = argparse.ArgumentParser(description='StackOverflow Spider')
    parser.add_argument('--o', type=str, default='question_list_spider', help='output file name')
    parser.add_argument('--l', type=str, default=str(10), help='page limit')
    parser.add_argument('--s', type=str, default=str(1), help='start page number')
    parser.add_argument('--p', type=str, default='./data/', help='data path')
    args = parser.parse_args()
    return args

def main():
    # sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    args = initArgParser()
    page_limit = args.l
    start_page_number = args.s
    output_file_full_name = args.p + args.o + time.strftime('_%y%m%d_%H%M%S') + '.json'

    if not (os.path.exists(args.p)):
        print('Data path "{}" does not exist. Creating...'.format(args.p))
        os.makedirs(args.p)
        print('Done!')
    if (os.path.exists(output_file_full_name)):
        print('Data file "{}" already exist. Removing...'.format(output_file_full_name))
        os.remove(output_file_full_name)
        print('Done!')

    execute(['scarpy', 'runspider', 'question_list_spider.py', '-a', 'limit='+page_limit,
            '-a', 'start='+start_page_number, '-o', output_file_full_name])
    return

if __name__ == '__main__':
    main()