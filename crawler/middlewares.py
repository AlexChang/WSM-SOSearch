from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from fake_useragent import UserAgent
import time
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError, TCPTimedOutError, ConnectionRefusedError
from scrapy.utils.python import global_object_name

import utils as F


class ChangeProxyRetryMiddleware(RetryMiddleware):

    def __init__(self, crawler):
        super(ChangeProxyRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            spider.logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            if isinstance(reason, TimeoutError) or isinstance(reason, TCPTimedOutError) or isinstance(
                    reason, ConnectionRefusedError) and not spider.direct_connection:
                # retryreq = self.change_request_proxy(request, spider)
                retryreq = spider.change_request_proxy(request)
                return retryreq
            # elif isinstance(reason, HttpError) and reason.value.response.status == 429:
            #     if not spider.direct_connection:
            #         retryreq = self.change_request_proxy(request, spider)
            #         return retryreq
            #     else:
            #         sleep_time = F.rand_int((180, 600))
            #         spider.logger.info('Meet 429 code! Sleep for {} seconds...'.format(sleep_time))
            #         self.crawler.engine.pause()
            #         time.sleep(sleep_time)
            #         spider.logger.info('Wake up!')
            #         self.crawler.engine.unpause()
            #         return request
            else:
                stats.inc_value('retry/max_reached')
                spider.logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                             {'request': request, 'retries': retries, 'reason': reason},
                             extra={'spider': spider})

    # def change_request_proxy(self, request, spider):
    #     # change proxy
    #     invalid_proxy = request.meta['proxy']
    #     spider.logger.info('Remove proxy {}'.format(invalid_proxy))
    #     spider.remove_invalid_proxy(invalid_proxy)
    #     if len(spider.proxy_addr_list) < spider.proxy_number:
    #         fetch_num = spider.proxy_number - len(spider.proxy_addr_list)
    #         spider.fetch_proxy_addr(num=fetch_num)
    #     request.meta['proxy'] = spider.get_proxy()
    #     return request


class TooManyRequestsRetryMiddleware(RetryMiddleware):

    def __init__(self, crawler):
        super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        elif response.status == 429:
            self.crawler.engine.pause()
            time.sleep(300)
            self.crawler.engine.unpause()
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response


class RandomUserAgentMiddleware(object):

    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        request.headers.setdefault("User-Agent", self.ua.random)
        # spider.logger.debug(request.headers.get('User-Agent'))
