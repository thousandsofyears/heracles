# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import redis as Redis

from mimir.config import Config
from werkzeug.local import LocalProxy
from mockredis import mock_strict_redis_client
from flask import current_app as app


REDIS_URL = Config.REDIS_URL
local_redis = Redis.StrictRedis.from_url(REDIS_URL)
mocked_redis = mock_strict_redis_client()


def get_redis():
    if app.config.get('TESTING', None):
        return mocked_redis
    else:
        return local_redis

redis = LocalProxy(get_redis)
