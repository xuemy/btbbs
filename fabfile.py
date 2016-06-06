#encoding:utf-8
from __future__ import unicode_literals

import fabtools
from fabric.api import *
from fabtools import require


@task
def superuser():
    env.hosts = ['vagrant@127.0.0.1:2222']

@task
def commentuser():
    env.hosts = ['xmy@127.0.0.1:2222']


@task
def create():
    require.users.create('xmy',password='xmy5650268')

@task
def setup():
    require.deb.packages([
        'python-dev',
        'python-pip',
        'libxml2-dev',
        'libxslt1-dev',
        'postgresql-server-dev-all',
    ])

    if not fabtools.user.exists('xmy'):
        require.users.create('xmy')

    require.python.packages([
            'scrapy',
            'django',
            'redis',
            'psycopg2',
            'django-qiniu-storage',
            'arrow',
            'gunicorn',
        ],
            # use_sudo=True
    )

    require.postgres.server()
    require.postgres.user('xuemy', 'xmy5650268')
    require.postgres.database('xuemy-db', 'xuemy')


    require.supervisor.process('xumy'

    )

    require.nginx.proxied_site()