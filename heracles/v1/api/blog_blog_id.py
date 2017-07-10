# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request, g

from . import Resource
from .. import schemas


class BlogBlogId(Resource):

    def get(self, blog_id):

        return {}, 200, None

    def put(self, blog_id):
        print(g.json)

        return None, 201, None

    def delete(self, blog_id):

        return None, 200, None