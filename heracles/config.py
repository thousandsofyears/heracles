# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from celery.schedules import crontab
from os import environ


class EnvConfigType(type):

    def __getattribute__(cls, key):
        value = object.__getattribute__(cls, key)
        env = environ.get(key)
        if env is not None:
            value = type(value)(env)
        return value


class Config(object):

    __metaclass__ = EnvConfigType

    DEBUG = True
    ERROR_404_HELP = False
    LISTEN = ''
    LISTEN_ON = ''

    SECRET = 'IMaRAY2ncfmI1Oqq'

    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@%s:%s/%s' % (
        environ.get('PG_USER', 'mimir'),
        environ.get('PG_PASSWORD', 'mmmm'),
        environ.get('PG_HOST', 'localhost'),
        environ.get('PG_PORT', '5432'),
        environ.get('PG_DATABASE', 'mimir'))
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ANALYSE_PG_USER = 'analyser'
    ANALYSE_PG_PASSWORD = 'aaaa'
    ANALYSE_PG_HOST = '10.0.80.11'
    ANALYSE_PG_PORT = '5432'
    ANALYSE_PG_DATABASE = 'analyser'

    # REDIS
    REDIS_URL = 'redis://%s:%s/%s' % (
        environ.get('REDIS_HOST', '10.0.80.11'),
        environ.get('REDIS_PORT', '6379'),
        environ.get('REDIS_DATABASE', '1'),
    )

    # CELERY
    CELERY_BROKER_URL = 'redis://%s:%s/%s' % (
        environ.get('REDIS_BROKER_HOST', 'localhost'),
        environ.get('REDIS_BROKER_PORT', '6379'),
        environ.get('REDIS_BROKER_DATABASE', '0'),
    )
    CELERY_RESULT_BACKEND = 'redis://%s:%s/%s' % (
        environ.get('REDIS_BROKER_HOST', 'localhost'),
        environ.get('REDIS_BROKER_PORT', '6379'),
        environ.get('REDIS_BROKER_DATABASE', '0'),
    )
    CELERY_ALWAYS_EAGER = False
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERYD_LOG_FILE = '/tmp/celery.log'
    CELERY_ENABLE_BEAT = True
    CELERYBEAT_SCHEDULE = {}
