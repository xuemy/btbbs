# encoding:utf-8
from __future__ import unicode_literals

import json
import re

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import permalink
from taggit.managers import TaggableManager

# Create your models here.
from bbs.utils import humanbytes

'''
year 年代
type 类型
area 地区
'''

detail_format = '''
                    <p class='original_title'>原名:{original_title}</p>
                    <p class='aka'>又名:{aka}</p>
                    <p class='cast'>主演:{cast}</p>
                    <p class='type'>类型:</p>
                    <p class='year'>年代:</p>
                    <p class='area'>地区:</p>
                    <p class='area'>片长:</p>
                    <p class='area'>上映时间:</p>
                    <p class='area'>语言:</p>
                    <p class='director'>导演:{director}</p>
                    <p class='writer>编剧:{writer}</p>
<p>
◎译　　名　星球大战7：原力觉醒/星球大：原力觉醒/星际大战七部曲：原力觉醒(台)<br>
◎片　　名　Star Wars: The Force Awakens<br>
◎年　　代　2015<br>
◎国　　家　美国<br>
◎类　　别　动作/科幻/奇幻/冒险<br>
◎语　　言　英语<br>
◎字　　幕　中英双字<br>
◎上映日期　2015-12-18(美国)/2016-01-09(中国大陆)<br>
◎IMDb评分  8.4/10 from 459,518 users<br>
◎豆瓣评分　7.2/10 from 94,122 users<br>
◎片　　长　135分钟<br>
◎导　　演　J·J·艾布拉姆斯 J.J. Abrams<br>
◎主　　演　黛西·雷德利 Daisy Ridley
　　　　　　约翰·博耶加 John Boyega
　　　　　　哈里森·福特 Harrison Ford
　　　　　　多姆纳尔·格里森 Domhnall Gleeson
　　　　　　亚当·德利弗 Adam Driver
　　　　　　马克·哈米尔 Mark Hamill
　　　　　　凯丽·费雪 Carrie Fisher
　　　　　　奥斯卡·伊萨克 Oscar Isaac
　　　　　　露皮塔·尼永奥 Lupita Nyong'o
　　　　　　安迪·瑟金斯 Andy Serkis
　　　　　　安东尼·丹尼尔斯 Anthony Daniels
　　　　　　彼德·梅犹 Peter Mayhew
　　　　　　马克斯·冯·叙多 Max von Sydow
　　　　　　比利·迪·威廉姆斯 Billy Dee Williams
　　　　　　爱德华·斯皮伊尔斯 Ed Speleers
　　　　　　马修·詹姆斯·托马斯 Matthew James Thomas
　　　　　　肯尼·贝克 Kenny Baker
　　　　　　格温多兰·克里斯蒂 Gwendoline Christie
　　　　　　西蒙·佩吉 Simon Pegg
　　　　　　克里斯塔·克拉克 Crystal Clarke
　　　　　　匹普·安德森 Pip Andersen
</p>
<p>◎简　　介</p>
<p></p>
'''
class Movie(models.Model):

    douban_id = models.IntegerField(unique=True)
    subtype = models.CharField(max_length=5, db_index=True, blank=True, choices=[('movie', '电影'),('tv', '电视剧')], verbose_name='分类', default='movie')
    name = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True, null=True)
    image = models.URLField(null=True, verbose_name='海报图')
    year = models.IntegerField(db_index=True, default=0, null=True, verbose_name='年代')
    rating = models.FloatField(db_index=True, default=0.0, null=True, verbose_name='豆瓣评分')
    summary = models.TextField(blank=True, verbose_name='简介')

    pubdate = models.DateField(null=True, verbose_name='上映时间')
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

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return ('detail', (), {
            'pk': self.id,
        })

    @property
    def get_image(self):
        return 'http://img.store.sogou.com/net/a/04/link?appid=100140019&url={}'.format(self.image)

    def get_torrents(self):
        torrents = self.torrent_t_set.all()
        regex = re.compile(r'(720p|1080p)',re.I)
        res = []
        for torrent in torrents:
            m = regex.search(torrent.name)
            if m:
                x = m.group()
            else:
                x = '高清'
            count = sum([d['size'] for d in json.loads(torrent.detail)])
            name = '【{}】.{}/{}.{}.torrent'.format(x,self.name,self.original_title,humanbytes(count))
            res.append(
                (name, torrent.id, torrent.etag, torrent.info_hash)
            )
        return res


    def info(self):
        pass
class Torrent(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    etag = models.CharField(max_length=40, unique=True)
    info_hash = models.CharField(max_length=40, unique=True)
    f = models.FileField()
    detail = models.TextField(null=True)
    views = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name


