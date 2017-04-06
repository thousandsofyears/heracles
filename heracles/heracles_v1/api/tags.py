# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class Tags(Resource):

    def get(self):
        print g.args

        return [], 200, None

    def post(self):
        print g.json

        return {}, 201, None