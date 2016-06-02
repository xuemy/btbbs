# encoding:utf-8
from __future__ import unicode_literals

import json
import os
from multiprocessing.dummy import Pool as ThreadPool

import arrow
import django
import pymongo
#
# mongodb
import re
from django.core.files.base import ContentFile
from django.db import connections, connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btbbs.settings")
django.setup()
from bbs.models import Movie
from init_db import add_intro, getLoger

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['movie']

x = db['x']
y = db['y']
movie_items = db['movie_items']
genres_map = {
    '脱口秀': ['Talk-Show'],
    '游戏节目': ['Game-Show'],
    '纪录片': ['紀錄片 Documentary', '紀錄片', 'Documentary'],
    '成人': ['Adult'],
}

def test_genres():
    s = set()
    for obj in x.find():
        genres = obj.get('genres')
        for g in genres:
            for k, v in genres_map.iteritems():
                if g in v:
                    g = k
            s.add(g)
        print "-".join(genres)
    print '+'.join(s)


def get_cast(casts):
    #获得主演信息

    if not isinstance(casts, list) or casts is None:
        return []
    return [x.get('name') for x in casts]

def get_director(directors):
    if not isinstance(directors, list) or directors is None:
        return
    return [x.get('name') for x in directors]
def get_genres(genres):
    if genres is None or not isinstance(genres, list):
        return
    r = []
    for g in genres:
        for k, v in genres_map:
            if g in v:
                g = k
        r.append(g)
    return r

def get_pubdata(pubdata):
    regex = re.compile(r'[\d-]+')
    res = []
    if not pubdata:
        return
    for p in pubdata:
        t = regex.findall(p)
        if t:
            try:
                d = arrow.get(t[0], ['YYYY-MM-DD','YYYY','YYYY-MM']).date()
                res.append(d)
            except:
                return None
    if res:
        return min(res)

def get_year(year):
    regex = re.compile(r'\d+')
    if not year:
        return
    r = regex.findall(year)
    if r:
        return r[0]

def parse_x(obj):
    subtype = obj.get('subtype')
    name = obj.get('title')
    original_title = obj.get('original_title')
    image = obj.get('images')['large']
    year = get_year(obj.get('year')) or 0
    rating = obj.get("rating")['average']
    countries = obj.get('countries', [])
    casts = get_cast(obj.get('casts'))
    directors = get_cast(obj.get('directors'))

    aka = obj.get('aka')
    genres = obj.get('genres')
    summary = obj.get('summary')

    res = locals()
    res.pop('obj')
    return res

def parse_y(obj):

    tags = get_cast(obj.get('tags'))

    attrs = obj.get('attrs')

    pubdate = get_pubdata(attrs.get('pubdate', []))
    language = attrs.get('language', [])
    movie_duration = attrs.get('movie_duration', [])
    writer = attrs.get('writer', [])
    res = locals()
    res.pop('obj')
    res.pop('attrs')
    return res


def move_data_to_postgresql():
    log = getLoger('move_to_postgresql')
    pool = ThreadPool(4)
    def func(x_obj):
        douban_id = x_obj['id']
        queryset = Movie.objects.filter(douban_id=douban_id)
        if not queryset.exists():
            log.info('开始处理数据{}'.format(douban_id))
            y_obj = y.find_one({'douban_id': douban_id})
            if not y_obj:
                print '#####{}'.format(douban_id)
                return
            item_obj = movie_items.find_one({'id': douban_id})
            if not item_obj:
                return
            x_dict = parse_x(x_obj)
            y_dict = parse_y(y_obj)

            name = x_dict['name']
            summary = x_dict['summary']
            relate_pic = item_obj['relate_pic']
            comments = item_obj['comments']
            intro = add_intro(title=name, summary=summary, intor_img=relate_pic['new'], intor_comment=comments)


            x_dict.update(y_dict)
            x_dict['intro'] = intro
            x_dict['douban_id'] = douban_id
            tags = x_dict.pop('tags')


            mt = Movie(**x_dict)
            mt.save()
            mt.tags.add(*tags)
            log.info('成功保存数据{}-{}'.format(douban_id, x_dict['name']))
    # pool.map(func, all_x)
    # pool.close()
    # pool.join()
    for x_obj in x.find():
        douban_id = x_obj['id']
        queryset = Movie.objects.filter(douban_id=douban_id)
        if not queryset.exists():
            log.info('开始处理数据{}'.format(douban_id))
            y_obj = y.find_one({'douban_id': douban_id})
            if not y_obj:
                print '#####{}'.format(douban_id)
                return
            item_obj = movie_items.find_one({'id': douban_id})
            if not item_obj:
                return
            x_dict = parse_x(x_obj)
            y_dict = parse_y(y_obj)

            name = x_dict['name']
            summary = x_dict['summary']
            relate_pic = item_obj['relate_pic']
            comments = item_obj['comments']
            intro = add_intro(title=name, summary=summary, intor_img=relate_pic['new'], intor_comment=comments)


            x_dict.update(y_dict)
            x_dict['intro'] = intro
            x_dict['douban_id'] = douban_id
            tags = x_dict.pop('tags')


            mt = Movie(**x_dict)
            mt.save()
            mt.tags.add(*tags)
            log.info('成功保存数据{}-{}'.format(douban_id, x_dict['name']))
        else:
            log.info('数据存在{}'.format(douban_id))


def move_Torrento_movie():
    torrent_cursor = connections['torrent'].cursor()
    movie_cursor = connection.cursor()
    torrent_cursor.execute('select * from torrent_info')
    description = [x[0] for x in torrent_cursor.description]
    res = torrent_cursor.fetchall()
    log = getLoger('move_to_postgresql')
    def f(r):
        res_dict = dict(zip(description, r))
        if not res_dict['etag'] or not res_dict['info_hash'] or not res_dict['key']:
            return
        query = Torrent.objects.filter(info_hash=res_dict['info_hash'])
        if query.exists():
            return
        else:
            m = Movie.objects.filter(douban_id=res_dict['douban_id']).first()
            if m:
                movie_cursor.execute("insert into bbs_Torrent (name, etag, info_hash, f, movie_id, detail) VALUES (%s,%s,%s,%s,%s,%s)",[
                    res_dict['name'],
                    res_dict['etag'],
                    res_dict['info_hash'],
                    './%s' %res_dict['key'],
                    m.id,
                    res_dict['detail']
                ])
                log.info('成功转移数据%s' % res_dict['name'])
    log.info('开始转移数据')
    map(f, res)
    # pool = ThreadPool(4)
    # pool.map(f, res)
    # pool.join()
    # pool.close()
# def remove_error_torrent():
#     torrents = Torrent.objects.all()
#     def remove(torrent):
#         try:
#             json.loads(torrent.detail)
#         except:
#             torrent.delete()
#     map(remove, torrents)

def move_tags():
    for y_obj in y.find():
        douban_id = y_obj['douban_id']
        queryset = Movie.objects.filter(douban_id=douban_id)
        if queryset.exists():
            m = queryset.first()
            y_dict = parse_y(y_obj)
            m.tags.add(*y_dict['tags'])

if __name__ == '__main__':
    # print parse_x(x.find_one())
    # test_genres()
    # print y.find_one({'douban_id':'53272688'})
    # move_data_to_postgresql()
    # t = Movie.objects.filter(genres__contains=['动作']).all()
    # print t
    # test_storage()
    # f = default_storage.open('three.txt')
    # print f.read()
    # t = T_Storage.objects.get()
    # print t.f.url
    # print t.f.read()

    # move_Torrento_movie()
    # isnull = Movie.objects.filter(Torrent__isnull=True).all()
    # for i in isnull:
    #     print i.name
    move_tags()