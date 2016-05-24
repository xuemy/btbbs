# encoding:utf-8
from __future__ import unicode_literals

import datetime
import logging
import os
import re

import django
from bson import ObjectId
from jinja2 import Template
from slugify import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btbbs.settings")
django.setup()
from bbs.models import Movie, Category
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['movie']


def parse_detail(detail):
    # detail = simplejson.loads(detail)
    return dict(
        id=detail.get('id'),
        name=detail.get('title'),
        area=detail.get('countries'),
        type=detail.get('genres'),
        cast=[t['name'] for t in detail.get('casts')],
        director=[t['name'] for t in detail.get('directors')],
        summary=detail.get('summary'),
        original_title=detail.get('original_title'),
        subtype=detail.get('subtype'),
        year=detail.get('year'),
        aka=detail.get('aka'),
        image=detail['images']['large'],
        rate_average=detail.get('rating')['average'],
        rate_count=detail.get('ratings_count'),
        # rating={
        #     'average': detail.get('rating')['average'],
        #     'min': detail.get('rating')['min'],
        #     'max': detail.get('rating')['max'],
        #     'count':detail.get('ratings_count')
        # },
    )


def get_html(detail):
    f = '''
<p>
    <img src="http://img.store.sogou.com/net/a/04/link?appid=100140019&url={image}" alt="">
</p>
<p>
    ◎译　　名　{aka}<br>
    ◎片　　名　{original_title}<br>
    ◎年　　代　{year}<br>
    ◎国　　家  {area}<br>
    ◎类　　别　{type}<br>
    ◎豆瓣评分　{rate_average}/10 from {rate_count} users<br>
    ◎导　　演　{director}<br>
    ◎主　　演　{cast}
</p>
<p>◎简　　介</p>
<p>{summary}</p>
'''
    d = {}
    for k, v in detail.iteritems():
        if isinstance(v, list):
            v = "/ ".join(v)
        d[k] = v

    return f.format(**d)


'''
class Files(models.Model):
    name = models.CharField(max_length=255)
    etag = models.CharField(max_length=40, unique=True)
    path = models.CharField(max_length=255)
    detail = models.TextField(verbose_name='文件主要内容', default='')
    ctime = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
'''


def add_type_slug():
    all_types = Type.objects.all()
    for t in all_types:
        if t.name == '电影':
            t.slug = 'movie'
            t.save()
        elif t.name == '电视剧':
            t.slug = 'tv'
            t.save()
        else:
            t.slug = slugify(t.name, separator="")
            t.save()


def add_intro(**kwargs):
    temp = '''
<div class="intro">
    <div class="intro_summary">
        <h2>{{title}}的剧情简介&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·</h2>
        <p>{{summary}}</p>
    </div>

    <div class="intro_img">
        <h2>{{title}}的海报和截图&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·</h2>
        <ul class="list-unstyled list-inline">
            {% for img in intor_img %}
                <li><img src="http://img.store.sogou.com/net/a/04/link?appid=100140019&url={{ img }}" alt="图片"></li>
            {% endfor %}
        </ul>
    </div>

    <div class="intro_comment">
        <h2>{{title}}的评论&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·&nbsp;&nbsp;·</h2>
        {% for foo in intor_comment %}
        <p class="comment_item">{{ foo }}</p>
        {% endfor %}
    </div>
</div>
    '''
    template = Template(temp)
    return template.render(kwargs)


def move_category():
    for m in db.movie_items.find():
        movie = Movie.objects.get(douban_id=m['id'])
        if not m['category']:
            category = Category.objects.get(name=u'电视剧')
            movie.category.add(category)
            movie.save()
        else:
            category = Category.objects.get(name=u'电影')
            cats = m['category']
            movie.category = map(lambda x: category.sons.get_or_create(name=x)[0], cats)

            movie.save()


def getLoger(log_name, level=logging.INFO, file_handler=False):
    """
    获取日志对象
    Args:
        :param log_name: string 日志对象名，即日志文件名
        :param level:  输出级别，写入级别为WARING
    Return:
        :return: 日志对象
    """
    # 创建一个logger
    logger = logging.getLogger(log_name)
    # 设置日志级别
    logger.setLevel(level)
    # 定义输出格式
    formatter = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s:%(message)s')

    if file_handler:
        # 创建文件处理器
        file_handler = logging.FileHandler('%s.log' % log_name.upper())
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 创建输出处理器
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # 给logger添加处理器

    return logger


FORMAT = [
    '%Y-%m-%d',
    '%Y-%m',
    '%Y',
]


def format_datetime(date_str):
    for f in FORMAT:
        try:
            return datetime.datetime.strptime(date_str, f).date()
        except:
            continue
    return None


SHOW_RE = re.compile(ur'首播:\s*(?P<time>[\d-]+)')


def add_shangyin():
    log = getLoger('add_show_time')
    error_log = getLoger('error', file_handler=True)

    def _add_show_time(movie):
        info = movie.info
        if info:
            log.info('开始创建ID:{} 的showtime'.format(movie.id))
            result = SHOW_RE.findall(info)
            if result:
                show_time = result[0]
                show_time_temp = format_datetime(show_time)
                if show_time_temp:
                    movie.show_time = show_time_temp
                    movie.save()
                    log.info('创建成功---SHOW_TIME：{}'.format(show_time))
                else:
                    error_log.info(
                        'ID:{0},douban_id:{1},name:{2},含有show_time 但是没有成功'.format(movie.id, movie.douban_id, movie.name)
                    )
            else:
                log.info('ID:{0}--NAME:{1}----DOUBAN:{2}没有show_time，无法创建'.format(movie.id, movie.name, movie.douban_id))

    map(_add_show_time, Movie.objects.filter(show_time=None).all())


def init_y_id():
    y = db['y']
    _re = re.compile(r'\/(\d+)')
    log = getLoger('init_y')
    def x(y_obj):
        douban_id = _re.findall(y_obj['id'])[0]
        y.update(
            {'_id': ObjectId(y_obj['_id'])},
            {'$set': {'douban_id': douban_id }}
        )
        log.info('成功 %s--%s' % (douban_id, y_obj['_id']))
    map(x, y.find())
def init_category():
    movie = Category.objects.get(name='电影')
    tv = Category.objects.get(name='电视剧')

    def func(obj):
        t = obj.get('subtype')
        try:
            m = Movie.objects.get(douban_id=obj['id'])
        except:
            return
        if t and t == 'movie':
            m.category = movie
            m.save()
        if t and t == 'tv':
            m.category = tv
            m.save()
    map(func, db.x.find())

if __name__ == '__main__':
    init_category()
    # init_y_id()
    # add_shangyin()
    # d = format_datetime('2016')
    # print type(d)
    # move_category()
    # movies = Movie.objects.all()
    # for movie in movies:
    #     torrents = movie.torrent.all()
    #     for torrent in torrents:
    #         back = Torrent_Back()
    #         back.name = torrent.name
    #         back.hash = torrent.hash
    #         back.etag = torrent.etag
    #         back.path = torrent.path
    #         back.detail = torrent.detail
    #         back.movie = movie
    #         try:
    #             back.save()
    #         except:
    #             continue


    # init_type()
    # add_thread()
    # print_subtype()
    # cursor = connections['torrent'].cursor()
    # cursor.execute('select * from douban_info limit 1')
    # res = cursor.fetchone()
    # print get_html(parse_detail(res[3]))

    # add_type_slug()
    # print Thread.objects.values('year').distinct().count()

    # m = db.movie_items.find_one()
    # cursor = connections['torrent'].cursor()
    #
    # cursor.execute('select douban_id,image_qiniu from douban_article')
    # for res in cursor.fetchall():
    #     try:
    #         movie = Movie.objects.get(douban_id=res[0])
    #         print movie.name
    #         movie.image = res[1]
    #         movie.save()
    #     except:
    #         continue

    # f = open('id.temp','w')
    # for m in db.movie_items.find():
    #     id = m['id']
    #     name = m['title']
    #     year = m['year']
    #     rating = m['rating']
    #     summary = m['summary']
    #     tags = m['tags']
    #     info = m['info']
    #
    #     comments = m['comments']
    #     reviews = m['reviews']
    #     all_photos = m['all_photos']
    #     relate_pic = m['relate_pic']
    #
    #     intro = add_intro(title = name, summary= summary, intor_img = relate_pic['new'],intor_comment= comments)
    #
    #
    #     movie = Movie()
    #     movie.name = name
    #     movie.year = year
    #     movie.rating = rating
    #     movie.summary = summary
    #     movie.info = info
    #     movie.douban_id = id
    #
    #     # print type(intro)
    #     movie_intro = Movie_intro(intro=intro)
    #     # movie_intro.movie = movie
    #     movie_intro.save()
    #     movie.intro = movie_intro
    #     movie.save()
    #     # def add_tag(x):
    #     #     c , _ = Tags.objects.get_or_create(name=x)
    #     #     return c
    #     # movie_tags = map(add_tag, tags)
    #     # print movie_tags
    #     for tag in tags:
    #         _tag = Tags.objects.filter(name=tag)
    #         if not _tag.exists():
    #             _tag = Tags(name=tag)
    #             _tag.save()
    #         else:
    #             _tag = _tag.first()
    #         movie.tags.add(_tag)
    #
    #     cursor.execute("select `name`,`info_hash`,`etag`,`detail`,`key` from torrent_info WHERE douban_id={0}".format(id))
    #
    #     for ress in cursor.fetchall():
    #         if not ress[2]:
    #             continue
    #         _file = Torrent.objects.filter(etag=ress[2])
    #         if not _file.exists():
    #             torrent = Torrent(
    #                 name=ress[0],
    #                 hash=ress[1],
    #                 etag=ress[2],
    #                 detail=ress[3],
    #                 path='http://7xqsqu.com1.z0.glb.clouddn.com/%s' % ress[4],
    #             )
    #             torrent.save()
    #         else:
    #             torrent = _file.first()
    #         movie.torrent.add(torrent)
    #
    #     movie.save()
    #     f.write("{0}\n".format(id))
    #     print '成功添加{0}'.format(name)
