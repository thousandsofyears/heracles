# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from heracles.database import db, Model, SurrogatePK, CSTDateTime
from heracles.timeutils import now


class Blog(SurrogatePK, Model):

    __tablename__ = 'blog'

    title = db.Column(db.String(128), nullable=False, unique=True)
    summary = db.Column(db.Unicode(256), nullable=False)
    is_published = db.Column(
        db.Boolean(), nullable=False, server_default=db.true())
    date_created = db.Column(CSTDateTime(
        timezone=True), nullable=False, default=now)
    date_modified = db.Column(CSTDateTime(
        timezone=True), nullable=False, default=now, onupdate=now)
