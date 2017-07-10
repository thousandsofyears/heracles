# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###
from __future__ import absolute_import

from .api.blog_blog_id import BlogBlogId
from .api.blogs import Blogs


routes = [
    dict(resource=BlogBlogId, urls=['/blog/<int:blog_id>'], endpoint='blog_blog_id'),
    dict(resource=Blogs, urls=['/blogs'], endpoint='blogs'),
]