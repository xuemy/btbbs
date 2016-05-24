#encoding:utf-8
import json
import os
import string

from qiniu import Auth, put_data
from qiniu.utils import etag_stream

from bbs.models import Movie

FILM_SUFFIX = [
    # windows 媒体
    '.asf', '.avi', '.wm', '.wmp', '.wmv',
    # real 媒体
    '.ram', '.m', '.rmvb', '.rpm', '.rt', '.smil', '.scm',
    # mpeg1/2媒体
    '.m1v', '.m2v', '.m2p', '.m2ts', '.mp2v', '.mpe', '.mpeg',
    '.mpeg1', '.mpeg2', '.mpg', 'mpv2', 'pva', '.tp', '.tpr', '.ts'
    # mpeg4媒体
    '.m4b', '.m4r', '.m4p', '.m4v', '.mp4', '.mpeg4',
    # 3GPP媒体
    '.3g2', '.3gp', '.3gp2', '.3gpp',
    # apple媒体
    '.mov', '.qt',
    # Flash媒体
    '.flv', '.f4v', '.swf', '.hlv',

    '.vob',
    # 视频文件
    '.amv', '.csf', '.divx', '.evo', '.mkv', '.mod', '.pmp', '.vp6', '.bik',
    '.mts', '.xvx', '.xv', '.xlmv', '.ogm', '.ogv', '.ogx',
    # 音频文件
    '.aac', '.ac3', '.acc', '.aiff', '.amr', '.ape', '.au', '.cda', '.dts', '.flac',
    '.m1a', '.m2a', '.m4a', '.mka', '.mp2', '.mp3', '.mpa', '.mpc', '.ra', '.tta',
    '.wav', '.wma', '.wv', '.mid', '.midi', '.ogg', '.oga',




]
    # 字幕文件
FILM_CAPTION = ['.srt', '.ass', '.ssa', '.smi', '.idx', '.sub', '.sup', 'psb', '.usf', '.ssf']
def file_extension(path):
  return os.path.splitext(path)[1]


def humanbytes(B):
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)

def is_film(path):
    if file_extension(path) in FILM_SUFFIX:
        return True
    return False

def is_film_caption(path):
    if file_extension(path) in FILM_CAPTION:
        return True

def get_torrent_film(torrent_detail):
    result = []
    for x in torrent_detail:
        name = string.lower(x['name'])
        size = x['size']
        if is_film(name):
            result.append({'name':name, 'size': size,'o_size':size})
    return result


def get_film_file(detail):
    return [{'name': d['name'], 'size': d['size']} for d in detail if is_film(string.lower(d['name']))]
def get_film_caption(detail):
    pass

def get_file_detail(detail):
    file_total = []
    film = []
    film_total = []
    caption = []
    caption_total = []
    for d in detail:
        name = string.lower(d['name'])
        size = d['size']
        file_total.append(size)
        if is_film(name):
            film.append(
                {'name':name,'size':size,'n_size':humanbytes(size)}
            )
            film_total.append(size)
        if is_film_caption(name):
            caption.append(
                {'name':name,'size':size, 'n_size':humanbytes(size)}
            )
            caption_total.append(size)

    return {
        'total':humanbytes(sum(file_total)),
        # 大小，文件数, 文件详情
        'sub': {
            'film': {
                'total': humanbytes(sum(film_total)),
                'files': film,
                'name':'视频文件',
                'have': True if film else False,
            },
            'caption': {
                'total':humanbytes(sum(caption_total)),
                'files':caption,
                'name':'字幕文件',
                'have': True if caption else False

            }
        }
    }

def parse_torrent(torrent):
    try:
        detail = json.loads(torrent.detail)
    except:
        return

def upload_to_qiniu(AK, SK, BUCKET_NAME,FILE_OBJ,FILE_NAME,):
    '''
    上传文件到七牛云，并返回 文件hash

    BUCKET_NAME 七牛资源空间名
    FILE_OBJ 文件二进制流
    FILE_NAME 文件保存到七牛云上的文件名
    '''
    q = Auth(AK, SK)
    token = q.upload_token(BUCKET_NAME, FILE_NAME, 3600)
    # ret
    # 一个dict变量，类似 {"hash": "<Hash string>", "key": "<Key string>"}
    # info
    """七牛HTTP请求返回信息类

    该类主要是用于获取和解析对七牛发起各种请求后的响应包的header和body。

    Attributes:
        status_code: 整数变量，响应状态码
        text_body:   字符串变量，响应的body
        req_id:      字符串变量，七牛HTTP扩展字段，参考 http://developer.qiniu.com/docs/v6/api/reference/extended-headers.html
        x_log:       字符串变量，七牛HTTP扩展字段，参考 http://developer.qiniu.com/docs/v6/api/reference/extended-headers.html
        error:       字符串变量，响应的错误内容
    """
    ret, info = put_data(token, FILE_NAME, FILE_OBJ)
    if info.status_code:
        if ret['hash'] == etag_stream(FILE_OBJ):
            return ret['hash']
        return None
    return None
def pagination(request, queryset, display_amount=15, after_range_num=5, bevor_range_num=4):

    paginator = Paginator(queryset, display_amount)
    page = request.GET.get('page')

    try:
        # 尝试获得分页列表
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    # 如果页数不存在
    except EmptyPage:
        # 获得最后一页
        objects = paginator.page(paginator.num_pages)

    _t = list(paginator.page_range)
    page = objects.number
    if page >= after_range_num:
        page_range = _t[page - after_range_num:page + bevor_range_num]
    else:
        page_range = _t[0:page + bevor_range_num]
    return objects, page_range
def hot_movie():
    objs = Movie.objects.exclude(torrent__isnull=True).exclude(show_time=None). \
               filter(category__name='电影').order_by('-show_time').all()[:12]
    return {
        'name': '电影',
        'objs': objs
    }


def hot_tv(request):
    objs_query = Movie.objects.exclude(torrent__isnull=True). \
               exclude(show_time=None).filter(category__name='电视剧'). \
               order_by('-show_time').all()
    objs, page_range = pagination(request, objs_query, display_amount=12)
    return {
        'name': '电视剧',
        'objs': objs
    }

if __name__ == '__main__':
    # s = '''[{"name": "Sinister.2012.720p.BluRay.X264-AMIABLE/Sinister.2012.720p.BluRay.X264-AMIABLE.mkv", "size": 4693301804}, {"name": "Sinister.2012.720p.BluRay.X264-AMIABLE/Sample/sinister.2012.720p.bluray.x264-amiable.sample.mkv", "size": 55269373}, {"name": "Sinister.2012.720p.BluRay.X264-AMIABLE/Subs/sinister.2012.720p.bluray.x264-amiable.subs.rar", "size": 1328525}, {"name": "Sinister.2012.720p.BluRay.X264-AMIABLE/Subs/sinister.2012.720p.bluray.x264-amiable.subs.sfv", "size": 58}]'''
    # print json.loads(s)
    # print get_torrent_film(json.loads(s))
    ak = 'jOCEgrOksRJIbggo-qp6dLujp3Vhjc7DzHmin3vs'
    sk = '-sn9yKeqdR7QYAVlMZZcDm4Ea44uI6sc4yc3IuJm'
    upload_to_qiniu(ak,sk,'xiyou-image','asdfsadfasdfasd','ceshiinfo.txt')