# -*- coding: utf-8 -*-
from flask import g

from . import Resource

from heracles.models import Blog


class Blogs(Resource):

    def get(self):
        limit = g.args['limit']
        page = g.args['page']

        pager = Blog.query.order_by(
            Blog.created_at.asc()
        ).paginate(page, limit, True)
        return pager.items, 200, {'X-Total-Page': pager.pages}
