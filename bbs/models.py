# encoding:utf-8
from __future__ import unicode_literals

import json
import re
import string

from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.db.models import permalink
from taggit.managers import TaggableManager
# Create your models here.
from bbs.utils import humanbytes



# pg_dump -d btbbs -h 127.0.0.1 -U postgres > bt2020.sql
# pg_dump -d btbbs -h 127.0.0.1 -U postgres -O -a -t bbs_movie -t bbs_torrent -t bbs_torrentinfo -t taggit_tag -t taggit_taggeditem > bt2020.sql
# pg_dump -d btbbs -h 127.0.0.1 -U postgres -O -s -t bbs_movie -t bbs_torrent -t bbs_torrentinfo -t taggit_tag -t taggit_taggeditem > bt2020_schem.sql

detail_format = '''
<p>◎译　　名 :星球大战7：原力觉醒/星球大：原力觉醒/星际大战七部曲：原力觉醒(台)</p>
<p>◎片　　名 :Star Wars: The Force Awakens</p>
<p>◎年　　代 :2015</p>
<p>◎国　　家 :美国</p>
<p>◎类　　别 :动作/科幻/奇幻/冒险</p>
<p>◎语　　言 :英语</p>
<p>◎字　　幕 :中英双字</p>
<p>◎上映日期 :2015-12-18(美国)/2016-01-09(中国大陆)</p>
<p>◎豆瓣评分 :7.2/10 from 94,122 users</p>
<p>◎片　　长 :135分钟</p>
<p>◎导　　演 :J·J·艾布拉姆斯 J.J. Abrams</p>
<p>◎主　　演 :</p>
'''

def get_torrent_type(filename):
    regex = re.compile(r'(720p|1080p)', re.I)
    m = regex.search(filename)
    if m:
        x = m.group()
    else:
        x = '高清'
    return x

class Movie(models.Model):

    douban_id = models.IntegerField(unique=True, db_index=True)
    subtype = models.CharField(max_length=5, db_index=True, blank=True, choices=[('movie', '电影'),('tv', '电视剧')], verbose_name='分类', default='movie')
    name = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True, null=True)
    image = models.URLField(null=True, verbose_name='海报图')
    year = models.IntegerField(db_index=True, default=0, null=True, verbose_name='年代')
    rating = models.FloatField(db_index=True, default=0.0, null=True, verbose_name='豆瓣评分')
    summary = models.TextField(blank=True, verbose_name='简介')

    pubdate = models.DateField(null=True, verbose_name='上映时间', db_index=True)
    intro = models.TextField(blank=True)

    views = models.IntegerField(default=1)

    tags = TaggableManager()

    genres = ArrayField(models.CharField(max_length=255), null=True, db_index=True, verbose_name='类型')
    language = ArrayField(models.CharField(max_length=255), null=True, db_index=True, verbose_name='语言', default=[])
    aka = ArrayField(models.CharField(max_length=255),  null=True, verbose_name='又名')
    countries = ArrayField(models.CharField(max_length=50), null=True, db_index=True, verbose_name='国家/地区')
    casts = ArrayField(models.CharField(max_length=255), null=True, db_index=True, verbose_name='主演')
    directors = ArrayField(models.CharField(max_length=255), null=True, db_index=True, verbose_name='导演')
    writer = ArrayField(models.CharField(max_length=255), null=True, db_index=True, verbose_name='编剧')
    movie_duration = ArrayField(models.CharField(max_length=255), null=True, db_index=True, verbose_name='片长')

    ctime = models.DateTimeField(auto_created=True, auto_now_add=True)

    _torrent_type = None
    _torrents = None

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = [
            '-pubdate', '-rating', '-ctime'
        ]


    @permalink
    def get_absolute_url(self):
        return ('detail', (), {
            'douban_id': self.douban_id,
        })


    @property
    def get_name(self):
        return '{name}/<small>{original_title}</small> [{year}] [{country}] [{genres}] [中文字幕] [{torrent_type}]'.format(
            name=self.name,
            original_title=self.original_title,
            year=self.year,
            country='/'.join(self.countries),
            genres='/'.join(self.genres),
            torrent_type = '/'.join(self.get_torrent_type)
        )
    @property
    def get_image(self):
        return 'http://img.store.sogou.com/net/a/04/link?appid=100140019&url={}'.format(self.image)

    def get_torrents(self):
        if self._torrents is None:
            torrents = self.torrent_set.all()
            # regex = re.compile(r'(720p|1080p)', re.I)
            res = []
            torrent_type = set()
            for _torrent in torrents:
                torrent = _torrent.torrentinfo
                x = get_torrent_type(torrent.name)
                torrent_type.add(string.lower(x))
                count = sum([d['size'] for d in json.loads(torrent.detail)])
                name = '【{}】.{}/{}.{}.{}.torrent'.format(x, self.name, self.original_title, '/'.join(self.genres),humanbytes(count))
                res.append(
                    dict(name=name, id=torrent.id, etag =torrent.etag, info_hash=torrent.info_hash)
                )
            self._torrent_type = list(torrent_type)
            self._torrents = res
        return self._torrents

    @property
    def get_torrent_type(self):
        if self._torrent_type is None:
            self.get_torrents()
        return self._torrent_type

    @classmethod
    def add_view(cls):
        cls.views += 1
        cls.save()

    @classmethod
    def get_genres(self):
        m = Movie.objects.raw('SELECT DISTINCT "unnest"(bbs_movie.genres) as genres from bbs_movie;',translations={"genres":'genres','id':'id'})
        return m

class Torrent_t(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    etag = models.CharField(max_length=40, unique=True)
    info_hash = models.CharField(max_length=40, unique=True)
    f = models.FileField()
    detail = models.TextField(null=True)
    views = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name

    class Meta:
        index_together = (
            ['etag','info_hash', 'id'],
        )


    def get_magnet(self):
        return 'magnet:?xt=urn:btih:{}'.format(self.info_hash)

class Torrent(models.Model):
    f = models.FileField()
    views = models.IntegerField(default=1)
    movie = models.ForeignKey(Movie)
    etag = models.CharField(max_length=40, unique=True)
    ctime = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.torrentinfo.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Torrent, self).save()

class TorrentInfo(models.Model):
    t = models.OneToOneField(Torrent, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    etag = models.CharField(max_length=40, unique=True)
    info_hash = models.CharField(max_length=40, unique=True)
    detail = models.TextField(null=True)
    ctime = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name

    @property
    def magnet(self):
        return 'magnet:?xt=urn:btih:{}'.format(self.info_hash)

    @property
    def download_url(self):
        #【BT天堂】【BTtiantang.com】[720p]死亡笔记.1.67GB
        site = get_current_site()
        filename = '[][]'



def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"

    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
def raw_sql_get_genres():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT "unnest"(bbs_movie.genres) as genres from bbs_movie;')
    return [row[0] for row in cursor.fetchall()]