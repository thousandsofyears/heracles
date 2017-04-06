# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import environ as _env


# 线上环境用Calypso 配置，所以做一个environ 的代理
class CalypsoEnv(object):
    def get(self, key, default=None):
        value = _env.get(key)

        # 相当于重定向
        alias = _env.get(value)
        if alias is not None:
            return alias

        if not value and default:
            return default
        return value

environ = CalypsoEnv()


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

    SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@%s:%s/%s' % (
        environ.get('PG_USER', 'heracles'),
        environ.get('PG_PASSWORD', 'hhhh'),
        environ.get('PG_HOST', 'localhost'),
        environ.get('PG_PORT', '5432'),
        environ.get('PG_DATABASE', 'heracles'))
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    REDIS_URL = 'redis://%s:%s/%s' % (
        environ.get('REDIS_HOST', 'localhost'),
        environ.get('REDIS_PORT', '6379'),
        environ.get('REDIS_DATABASE', '1'),
    )

    DOMAIN = 'dev.heracles.wishstone.in'
    LISTEN = '0.0.0.0'
    LISTEN_ON = 6239
