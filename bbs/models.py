# encoding:utf-8

from django.db import models
from django.db.models import permalink

# Create your models here.
'''
year 年代
type 类型
area 地区
'''

detail_format = '''
                    <p class='original_title'>原名:{original_title}</p>
                    <p class='aka'>又名:{aka}</p>
                    <p class='cast'>主演:{cast}</p>
                    <p class='director'>导演:{director}</p>
                    <p class='writer>编剧:{writer}</p>
                    <p class='type'>类型:</p>
                    <p class='year'>年代:</p>
                    <p class='area'>地区:</p>
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



class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True, unique=True)
    parent = models.ForeignKey('self', models.SET_NULL,blank=True,null=True,related_name='sons')

# @receiver(post_migrate)
# def init_category(sender, **kwargs):
#     init_ = ['电影', '电视剧', '综艺', '音乐', '图书', '软件']
#     Category.objects.bulk_create([Category(name=x) for x in init_])



class Torrent_b(models.Model):
    name = models.CharField(max_length=255)
    hash = models.CharField(max_length=40, db_index=True, unique=True)
    etag = models.CharField(max_length=40, unique=True)
    path = models.CharField(max_length=255)
    detail = models.TextField(verbose_name='文件主要内容', default='', null=True)
    ctime = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return ('download',(),{
            # 'tid': self.movie_set.,
        })

class Tags(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return ('tag', (), {
            'tag_name': self.name,
        })
class Torrent(models.Model):
    name = models.CharField(max_length=255)
    hash = models.CharField(max_length=40, db_index=True, unique=True)
    etag = models.CharField(max_length=40, unique=True)
    path = models.CharField(max_length=255)
    detail = models.TextField(verbose_name='文件主要内容', default='', null=True)
    ctime = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name
    class Meta:
        index_together = [
            ['id','etag']
        ]

    @permalink
    def get_absolute_url(self):
        return ('download',(),{
            'tid': self.movie_id,
        })


class Movie(models.Model):
    name = models.CharField(max_length=255)
    year = models.IntegerField(db_index=True, default=0, null=True)
    rating = models.FloatField(db_index=True, default=0.0, null=True)
    views = models.IntegerField(default=0)
    image = models.CharField(max_length=255,blank=True,null=True)
    show_time =  models.DateField(null=True)
    ctime = models.DateTimeField(auto_now_add=True)
    utime = models.DateTimeField(auto_now=True)
    summary = models.TextField(null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    intro = models.OneToOneField('Movie_intro', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags)
    # torrent = models.ManyToManyField(Torrent)
    douban_id = models.IntegerField(null=True, db_index=True)
    category = models.ForeignKey(Category, null=True)
    # subcategory = models.ManyToManyField(Category)

    def __unicode__(self):
        return self.name

    class Meta:
        index_together = [

        ]

        ordering = ['-year', '-ctime']
        
    @permalink
    def get_absolute_url(self):
        return ('detail', (), {
            'pk': self.id,
        })
class Movie_intro(models.Model):
    intro = models.TextField(null=True, default="")
    # movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
