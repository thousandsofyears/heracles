# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class CategoryCategoryId(Resource):

    def get(self, category_id):

        return {}, 200, None

    def put(self, category_id):
        print g.json

        return None, 201, None

    def delete(self, category_id):

        return None, 200, None