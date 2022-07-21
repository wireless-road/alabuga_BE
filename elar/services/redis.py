# -*- coding: utf-8 -*-
from flask import current_app
from redis import StrictRedis
import json


class RedisService():
    """
    An helper class to communicate with Redis cache.
    """

    def __init__(self, redis_uri):
        self.redis_uri = redis_uri
        self.redis = StrictRedis.from_url(self.redis_uri)

    def deny_token(self, token):
        """
        mark token as expired.
        notes: ttl must be greater or equal token expired time.
        """
        self.redis.setex(token, current_app.config['TOKEN_EXPIRE_TIME'], json.dumps({
            'expired': True
        }))

    def is_token_denied(self, token):
        """
        check if token is marked as denied.
        """
        data = self.redis.get(token)
        if data:
            return json.loads(data).get('expired') is True
        return False

    def get(self, name):
        return self.redis.get(name)

    def setex(self, name, time, value):
        return self.redis.setex(name, time, value)
