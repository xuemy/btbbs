# -*- coding: utf-8 -*-
import os

import qiniu
import requests
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.encoding import force_text


def setting(name, default=None):
    """
    Helper function to get a Django setting by name or (optionally) return
    a default (or else ``None``).
    """
    return getattr(settings, name, default)

class QiniuStorage(Storage):
    access_key = setting('QINIU_ACCESS_KEY')
    secret_key = setting('QINIU_SECRET_KEY')
    bucket_name = setting('QINIU_BUCKET_NAME')
    bucket_domain = 'http://7xqsqu.com1.z0.glb.clouddn.com'

    def __init__(self, *args, **kwargs):
        super(QiniuStorage, self).__init__(*args, **kwargs)
        self._auth = None
        self._bucket = None
        self._stat = None
        self._exist = None



    @property
    def auth(self):
        if self._auth is None:
            self._auth = qiniu.Auth(self.access_key,self.secret_key)
        return self._auth

    @property
    def bucket(self):
        if self._bucket is None:
            self._bucket = qiniu.BucketManager(self.auth)
        return self._bucket


    def get_stat(self, name):
        if self._stat is None:
            self._stat, ResponseInfo = self.bucket.stat(self.bucket_name, name)
            # if ResponseInfo.status_code != 200:
            #     self._exist = False
            # else:
            #     self._exist = True
        return self._stat

    def path(self, name):
        return os.path.normpath(name)
    def get_available_name(self, name, max_length=None):
        return name

    def size(self, name):
        return self.get_stat(name)['fsize']

    def exists(self, name):
        return self.get_stat(name) is not None

    def delete(self, name):
        self.bucket.delete(self.bucket_name, name)

    def _open(self, name, mode='rb'):
        content = requests.get(self.url(name)).content
        return ContentFile(content, name)

    def _save(self, name, content):
        token = self.auth.upload_token(self.bucket_name, name)
        if hasattr(content, 'chunks'):
            content_data = b''.join(chunk for chunk in content.chunks())
        else:
            content_data = content.read()
        qiniu.put_data(token, name, content_data)
        return name

    def save(self, name, content, max_length=None):
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content)

        name = self._save(name, content)

        # Store filenames with forward slashes, even on Windows
        return force_text(name.replace('\\', '/'))

    def url(self, name):
        return '{}/{}'.format(self.bucket_domain, self.get_valid_name(name))





class QiniuFile(File):


    def size(self):
        pass
    def read(self):
        pass
    def write(self):
        pass
    def close(self):
        pass