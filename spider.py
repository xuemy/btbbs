# encoding:utf-8
import json
import os
import string
import urllib

import django
import scrapy
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess

from init_db import add_intro
from test_data import parse_x, parse_y

BASE_DIR = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btbbs.settings")
django.setup()

from bbs.models import Movie

bt_search = 'http://www.bttiantang.com/s.php?q={}&sitesearch=www.bttiantang.com&domains=bttiantang.com&hl=zh-CN&ie=UTF-8&oe=UTF-8'


class ObjItem(scrapy.Item):
    obj = scrapy.Field()


class UpdatePipeline(object):
    def process_item(self, item, spider):
        obj = item['obj']
        queryset = Movie.objects.filter(douban_id=obj['douban_id'])
        if not queryset.exists():
            tags = obj.pop('tags')
            m = Movie(**obj)
            m.save()
            m.tags.add(*tags)
        else:
            m = queryset.first()
            if not m.intro:
                m.intro = obj['intro']
                m.save()
        return item


class UpdateSpider(Spider):
    name = 'update'
    start_urls = [
        'https://movie.douban.com/j/search_subjects?type=movie&tag=%E6%9C%80%E6%96%B0&page_limit=20&page_start=0'
    ]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
        'COOKIES_ENABLED': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
        },
        'ITEM_PIPELINES': {
            'spider.UpdatePipeline': 300,
        },
        'DOWNLOAD_DELAY': 1.5,
    }

    def parse(self, response):
        json_obj = json.loads(response.text)
        for obj in json_obj['subjects']:
            douban_id = obj['id']
            x_api_url = 'http://api.douban.com/v2/movie/subject/{}?apikey=0cf8ec0e01250eeb26eac42a036f2cc1'.format(
                douban_id)
            y_api_url = 'https://api.douban.com/v2/movie/{}?apikey=0cf8ec0e01250eeb26eac42a036f2cc1'.format(douban_id)
            yield Request(x_api_url, callback=self.parse_X_API,
                          meta={'douban_id': douban_id, 'y_api_url': y_api_url, 'url': obj['url']})

    def parse_X_API(self, response):
        y_api_url = response.meta['y_api_url']
        x_obj = parse_x(json.loads(response.text))
        x_obj['douban_id'] = response.meta['douban_id']
        yield Request(y_api_url, callback=self.parse_Y_API, meta={'x_obj': x_obj, 'url': response.meta['url']})

    def parse_Y_API(self, response):
        x_obj = response.meta['x_obj']
        y_obj = parse_y(json.loads(response.text))
        x_obj.update(y_obj)

        url = response.meta['url']
        yield Request(url=url, callback=self.parse_douban, meta={'x_obj': x_obj})

    def parse_douban(self, response):
        origin_relate_pic = response.xpath('//div[@id="related-pic"]//img/@src').extract()
        new_relate_pic = [string.replace(o, 'albumicon', 'photo') for o in origin_relate_pic]

        relate_pic = {
            'origin': origin_relate_pic,
            'new': new_relate_pic,
        }
        x_obj = response.meta['x_obj']
        name = x_obj['name']
        summary = x_obj['summary']
        comments = response.xpath('//div[@id="hot-comments"]/div[@class="comment-item"]//p/text()').extract()
        intro = add_intro(title=name, summary=summary, intor_img=relate_pic['new'], intor_comment=comments)
        x_obj['intro'] = intro
        item = ObjItem()
        item['obj'] = x_obj
        yield item

        yield Request(
            url=bt_search.format(urllib.unquote(name)), callback=self.parse_bt_search, meta={'douban_id': x_obj['douban_id']}
        )

    def parse_bt_search(self, response):

        pass

if __name__ == '__main__':
    # runner = CrawlerRunner()
    #
    # d = runner.crawl(UpdateSpider)
    # d.addBoth(lambda _: reactor.stop())
    # reactor.run()
    process = CrawlerProcess()
    process.crawl(UpdateSpider)
    process.start()
