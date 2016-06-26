# encoding:utf-8
import json
import os
import random
import re
import string
import urllib
import urlparse
from time import sleep

import django
import libtorrent
import scrapy
from django.core.files.base import ContentFile
from qiniu.utils import etag_stream
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from init_db import add_intro
from test_data import parse_x, parse_y

BASE_DIR = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btbbs.settings")
django.setup()

from bbs.models import Movie, Torrent, TorrentInfo

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
            return item
        else:
            m = queryset.first()
            if not m.intro:
                m.intro = obj['intro']
                m.save()


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
            url=bt_search.format(urllib.unquote(name)), callback=self.parse_bt_search,
            meta={'douban_id': x_obj['douban_id']}
        )

    def parse_bt_search(self, response):
        pass


class FromBTtiantang(CrawlSpider):
    name = 'bttiantang'
    start_urls = [
        # 'http://www.bttiantang.com',
        'http://www.bttiantang.com/?PageNo=1',
        'http://www.bttiantang.com/?PageNo=2',
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
    rules = (
        # 提取匹配 'category.php' (但不匹配 'subsection.php') 的链接并跟进链接(没有callback意味着follow默认为True)
        # Rule(LinkExtractor(allow=('\/\?PageNo=(\d+)',))),

        # 提取匹配 'item.php' 的链接并使用spider的parse_item方法进行分析
        Rule(LinkExtractor(allow=('\/subject\/(\d+).html',), restrict_xpaths=('//div[@class="ml"]',)),
             callback='parse_item'),
    )

    def parse_item(self, response):
        # 获取采集站电影列表
        self.log(u'获取到URL:{}'.format(response.url))
        torrents = LinkExtractor(restrict_xpaths=('//div[@class="tinfo"]')).extract_links(response)
        self.log(u'从URL:{}，获取到{}个种子文件'.format(response.url, len(torrents)))

        douban_url_temp = LinkExtractor(allow=('\/jumpto\.php\?aid=(\d+)')).extract_links(response)
        if douban_url_temp:
            self.log(u'开始获取电影豆瓣ID，URL:{}'.format(response.url))
            url = douban_url_temp[0].url
            yield Request(url=url, callback=self.get_douban_id, meta={'torrents': torrents})

    def get_douban_id(self, response):
        regex = re.compile(r"/subject/(\d+)/")
        key_temp = regex.findall(response.body)
        if key_temp:
            key = key_temp[0]
            self.log(u'得到豆瓣ID：{}'.format(key))
            douban_id = key
            x_api_url = 'http://api.douban.com/v2/movie/subject/{}?apikey=0cf8ec0e01250eeb26eac42a036f2cc1'.format(
                douban_id)
            y_api_url = 'https://api.douban.com/v2/movie/{}?apikey=0cf8ec0e01250eeb26eac42a036f2cc1'.format(douban_id)

            yield Request(x_api_url, callback=self.parse_X,
                          meta={'y_api': y_api_url, 'douban_id': douban_id, 'torrents':response.meta['torrents']})


    def parse_X(self, response):
        self.log(u'从X——api获得了数据')
        x_obj = parse_x(json.loads(response.text))
        x_obj['douban_id'] = response.meta['douban_id']
        yield Request(
            response.meta['y_api'],
            callback=self.parse_Y,
            meta={
                'x_obj': x_obj,
                'douban_id':response.meta['douban_id'],
                'torrents':response.meta['torrents']
            }
        )

    def parse_Y(self, response):
        self.log(u'从Y——api获得了数据')
        y_obj = parse_y(json.loads(response.text))
        x_obj = response.meta['x_obj']
        x_obj.update(y_obj)
        yield Request(
            url='https://movie.douban.com/subject/{}/'.format(response.meta['douban_id']),
            callback=self.parse_douban,
            meta={
                'torrents': response.meta['torrents'],
                'obj': x_obj,
                'douban_id': response.meta['douban_id'],
            }
        )

    def parse_douban(self, response):
        self.log(u'从豆瓣主页获得了数据')
        origin_relate_pic = response.xpath('//div[@id="related-pic"]//img/@src').extract()
        new_relate_pic = [string.replace(o, 'albumicon', 'photo') for o in origin_relate_pic]

        relate_pic = {
            'origin': origin_relate_pic,
            'new': new_relate_pic,
        }
        x_obj = response.meta['obj']
        name = x_obj['name']
        summary = x_obj['summary']
        comments = response.xpath('//div[@id="hot-comments"]/div[@class="comment-item"]//p/text()').extract()
        intro = add_intro(title=name, summary=summary, intor_img=relate_pic['new'], intor_comment=comments)

        x_obj['intro'] = intro

        item = ObjItem()
        item['obj'] = x_obj
        yield item

        torrnets = response.meta['torrents']

        def get_args(url):
            query_arg = urlparse.parse_qsl(urlparse.urlparse(url).query)
            tmp = {k: v for k, v in query_arg}
            return {
                "action": "download",
                "id": tmp['id'],
                "uhash": tmp['uhash']
            }

        for torrent in torrnets:
            arg = get_args(torrent.url)
            url = "http://www.bttiantang.com/download%s.php" % random.choice([1, 2, 3, 4])
            yield scrapy.FormRequest(
                url=url,
                formdata=arg,
                callback=self.parse_torrent,
                meta={
                    'douban_id': response.meta['douban_id']
                }
            )

    def parse_torrent(self, response):
        lt = libtorrent.torrent_info(libtorrent.bdecode(response.body))
        info_hash = '%s' % lt.info_hash()
        name = lt.name()
        details = json.dumps([{"name": f.path, "size": f.size} for f in lt.files()])

        content = ContentFile(response.body, name=u'{}.torrent'.format(info_hash))
        etag = etag_stream(content)

        exist = Torrent.objects.filter(etag=etag).exists()
        if exist:
            self.log(u'的种子文件：{} 存在'.format(info_hash))
            return

        flag = True
        t = 0
        self.log(u'开始保存ID：{}，的种子文件：{}'.format(response.meta['douban_id'], info_hash))
        while flag:
            try:
                movie = Movie.objects.get(douban_id=response.meta['douban_id'])
            except:
                sleep(3)
                t += 1
                if t < 3:
                    continue
                else:
                    flag = False
            # 确保种子保存成功
            try:
                t = Torrent()
                t.movie = movie
                t.etag = etag
                t.f = content
                # t.f.save(u'{}.torrent'.format(info_hash), content, save=False)
                t.save()
            except Exception, e:
                self.log(e)
                flag = False
                return
            # 确保种子信息保存成功
            try:
                t_info = TorrentInfo()
                t_info.name = name
                t_info.info_hash = info_hash
                t_info.etag = etag
                t_info.detail = details
                t_info.t = t
                t_info.save()
            except Exception, e:
                self.log(e)
                flag = False
                return
        self.log(u'保存成功ID：{}，的种子文件：{}'.format(response.meta['douban_id'], info_hash))

if __name__ == '__main__':
    # runner = CrawlerRunner()
    #
    # d = runner.crawl(UpdateSpider)
    # d.addBoth(lambda _: reactor.stop())
    # reactor.run()
    process = CrawlerProcess()
    process.crawl(FromBTtiantang)
    process.start()
