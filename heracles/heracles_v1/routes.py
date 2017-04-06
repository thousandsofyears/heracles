# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from .api.categorys import Categorys
from .api.blog_blog_id import BlogBlogId
from .api.category_category_id import CategoryCategoryId
from .api.tag_tag_id import TagTagId
from .api.blogs import Blogs
from .api.tags import Tags


routes = [
    dict(resource=Categorys, urls=['/categorys'], endpoint='categorys'),
    dict(resource=BlogBlogId, urls=['/blog/<blog_id>'], endpoint='blog_blog_id'),
    dict(resource=CategoryCategoryId, urls=['/category/<category_id>'], endpoint='category_category_id'),
    dict(resource=TagTagId, urls=['/tag/<tag_id>'], endpoint='tag_tag_id'),
    dict(resource=Blogs, urls=['/blogs'], endpoint='blogs'),
    dict(resource=Tags, urls=['/tags'], endpoint='tags'),
]