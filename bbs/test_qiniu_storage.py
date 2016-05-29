# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth
from qiniu import BucketManager

access_key = 'jOCEgrOksRJIbggo-qp6dLujp3Vhjc7DzHmin3vs'
secret_key = '-sn9yKeqdR7QYAVlMZZcDm4Ea44uI6sc4yc3IuJm'

#初始化Auth状态
q = Auth(access_key, secret_key)

#初始化BucketManager
bucket = BucketManager(q)

#你要测试的空间， 并且这个key在你空间中存在
bucket_name = 'torrent'
key = 'python-logo.png'

#获取文件的状态信息
ret, info = bucket.stat(bucket_name, key)
dret, dinfo = bucket.delete(bucket_name,key)
print(info)
print info.status_code
print type(info.status_code)
print ret


print '=='
print dret
print dinfo