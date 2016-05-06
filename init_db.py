#encoding:utf-8
from __future__ import unicode_literals

import os

import django
from jinja2 import Template
from slugify import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btbbs.settings")
django.setup()
from django.db import connections
import simplejson
from bbs.models import Movie, Category
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['movie']

def init_type():
    t = Type(name='电影')
    t2 = Type(name='电视剧')
    t.save()
    t2.save()

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
        if isinstance(v,list):
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
def add_thread():
    cursor = connections['torrent'].cursor()
    cursor.execute('select * from douban_info')
    for res in cursor.fetchall():
        try:
            detal = simplejson.loads(res[3])
        except:
            continue
        detal = parse_detail(detal)
        message = get_html(detal)
        _t = Thread.objects.filter(uuid=detal['id'])
        if _t.exists():
            t = _t.first()
        else:
            t = Thread(
                uuid=detal['id'],
                name=detal.get('name'),
                year=detal.get('year', 0),
            )
            try:
                t.save()
            except:
                continue
            post = Post(massage=message)
            post.thread= t
            post.save()
        subtype = detal.get('subtype')
        if subtype == 'movie':
            t1 = Type.objects.get(name='电影')
        else:
            t1 = Type.objects.get(name='电视剧')

        types = detal.get('type')
        if types:
            for type in types:
                _type, created = Type.objects.get_or_create(name=type, parent=t1)
                # if created:
                t.types.add(_type)
        area = detal.get('area')
        if area:
            for a in area:
                _a, created = Area.objects.get_or_create(name=a)
                # if created:
                t.area.add(_a)
        cursor.execute("select `name`,`info_hash`,`etag`,`detail`,`key` from torrent_info WHERE douban_id={0}".format(detal['id']))
        for ress in cursor.fetchall():
            if not ress[2]:
                continue
            _file = Files.objects.filter(etag=ress[2])
            if not _file.exists():
                _file = Files(
                    name=ress[0],
                    etag=ress[2],
                    path = 'http://7xqsqu.com1.z0.glb.clouddn.com/%s' % ress[4],
                    detail=ress[3]
                )
                _file.save()
            else:
                _file = _file.first()
            t.files.add(_file)
        t.save()
        # print('成功添加电影 %s'.encode('gb2312') % detal['name'])



def print_subtype():
    cursor = connections['torrent'].cursor()
    cursor.execute('select * from douban_info')
    for res in cursor.fetchall():
        try:
            detail = simplejson.loads(res[3])
        except:
            continue
        detail = parse_detail(detail)
        # print detail
        subtype = detail.get('subtype')
        if subtype and subtype != 'movie':
            print subtype, detail['id'], detail['name']
        # if detail.get['subtype'] and detail.get['subtype'] != 'movie':
        #     print (detail.get['subtype'],detail['id'],detail['name'])

def add_type_slug():
    all_types = Type.objects.all()
    for t in all_types:
        if t.name == '电影':
            t.slug = 'movie'
            t.save()
        elif t.name=='电视剧':
            t.slug = 'tv'
            t.save()
        else:
            t.slug = slugify(t.name,separator="")
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
            category = Category.objects.get(name = u'电视剧')
            movie.category.add(category)
            movie.save()
        else:
            category = Category.objects.get(name = u'电影')
            cats = m['category']
            movie.category= map(lambda x : category.sons.get_or_create(name=x)[0],cats)

            movie.save()

if __name__ == '__main__':
    move_category()
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
    #for m in db.movie_items.find():
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


