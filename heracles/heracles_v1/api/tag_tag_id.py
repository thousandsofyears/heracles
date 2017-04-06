# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class TagTagId(Resource):

    def get(self, tag_id):

        return {}, 200, None

    def put(self, tag_id):
        print g.json

        return None, 201, None

    def delete(self, tag_id):

        return None, 200, None