# -*- coding: utf-8 -*-
from datetime import datetime

import json
import re as _re
import math as _math
import pytz as _pytz
from functools import partial
from datetime import tzinfo as _tzinfo, timedelta

from sqlalchemy import orm
from sqlalchemy.util import OrderedDict
from flask.helpers import locked_cached_property
from flask_sqlalchemy import SQLAlchemy as _SA
from flask_sqlalchemy import SignallingSession, _EngineConnector, get_state
from pytz import ZERO
from sqlalchemy.types import TypeDecorator, DateTime, LargeBinary
from sqlalchemy.ext.mutable import Mutable, MutableDict

from timeutils import cst


def copy_inst(fromobj, tocls, keys, **extra_kw):
    kwargs = dict((key, getattr(fromobj, key)) for key in keys)
    kwargs.update(extra_kw)
    return tocls(**kwargs)


class PreserveDeleted(object):
    """Preserve deleted decorator

    Tracks "deleted" objects and includes a "restore" feature which will
    "restore" a given row back to the main table.

    Inspired by http://stackoverflow.com/a/13259889, Thanks to zzzeek.

    :Usage

    @db.preserve_deleted(reason=db.Column(db.String(256)))
    class A(db.Model):
        __tablename__ = 'a'

        id = db.Column(db.Integer(), primary_key=True)
        data1 = db.Column(db.String(256))
        data2 = db.Column(db.Text())

    a1, a2 = \
        A(data1='a1d1', data2='a1d2'), \
        A(data1='a2d1', data2='a2d2')

    db.session.add_all([a1, a2])
    db.session.commit()

    assert A.query.order_by(A.id).count() == 2

    db.session.delete(a1, reason='for_fun')
    db.session.commit()

    assert A.query.order_by(A.id).count() == 1

    a1_deleted = A.deleted.query.get(1)
    a1_deleted.restore()
    db.session.commit()

    assert A.deleted.query.count() == 0
    assert A.query.order_by(A.id).count() == 2

    """
    def __init__(self, db, *extra_cols, **kw_extra_cols):
        self.db = db
        self.extra_cols = list(extra_cols)
        if kw_extra_cols:
            for key, col in kw_extra_cols.iteritems():
                if col.key is None:
                    col.key = key
                if col.name is None:
                    col.name = key
                self.extra_cols.append(col)

    def copy_col(self, col):
        newcol = col.copy()
        newcol.constraints = set()
        return newcol

    def __call__(self, class_):

        keys = class_.__table__.c.keys()
        cols = OrderedDict(
            (col.key, self.copy_col(col)) for col in class_.__table__.c)
        for extra_col in self.extra_cols:
            cols[extra_col.key] = extra_col
        cols['__tablename__'] = '%s_deleted' % class_.__table__.name

        db = self.db

        class History(object):
            def restore(self):
                db.session.delete(self)
                instance = copy_inst(self, class_, keys)
                db.session.add(instance)
                instance._deleted = self
                return instance

        hist_class = type(b'%sDeleted' % class_.__name__,
                          (History, db.Model),
                          cols)

        class_.deleted = hist_class

        return class_

class _SignallingSession(SignallingSession):
    def __init__(self, *args, **kwargs):
        super(_SignallingSession, self).__init__(*args, **kwargs)

    def get_bind(self, mapper, clause=None):
        # 增加 master/slave 支持
        # mapper is None if someone tries to just get a connection

        if mapper is not None:
            info = getattr(mapper.mapped_table, 'info', {})
            bind_key = info.get('bind_key')
            if bind_key is not None:
                state = get_state(self.app)
                return state.db.get_engine(self.app, bind=bind_key)

        # 通过全局变量 _disable_db_slaves 来控制 slave 行为
        # 不在 request context 内的读操作一律使用主库
        #if g and not hasattr(g, 'disable_db_slaves') and \
        #   isinstance(clause, sql.Select):
        #    state = get_state(self.app)
        #    return state.db.get_engine(self.app, bind='__slave__')

        return super(_SignallingSession, self).get_bind(mapper, clause)

    def delete(self, instance, **extra_kw):
        # 扩展 delete 方法, 在 preserve_deleted 激活时可以传递 extra_cols 的值
        class_ = instance.__class__
        if hasattr(class_, 'deleted'):
            keys = class_.__table__.c.keys()
            h = copy_inst(instance, class_.deleted, keys, **extra_kw)
            self.add(h)

        return super(_SignallingSession, self).delete(instance)


class SQLAlchemy(_SA):
    def __init__(self, *args, **kwargs):
        super(SQLAlchemy, self).__init__(*args, **kwargs)

    def init_app(self, app):
        # 增加 master/slaves 支持
        app.config.setdefault('SQLALCHEMY_DATABASE_SLAVE_URIS', None)
        config_binds = app.config.get('SQLALCHEMY_BINDS')
        if config_binds and '__slave__' in config_binds:
            raise KeyError('__slave__ is a reserved word.')

        return super(SQLAlchemy, self).init_app(app)

    def create_scoped_session(self, options=None):
        """Hepler factory method that creates a scoped session.

        See: https://github.com/mitsuhiko/flask-sqlalchemy/issues/64

        """
        if options is None:
            options = {}
        scopefunc = options.pop('scopefunc', None)
        db = self

        class PartialSignallingSession(_SignallingSession):

            def __init__(self, autocommit=False, autoflush=False):
                (super(PartialSignallingSession, self)
                 .__init__(db, autocommit, autoflush, **options))

        return orm.scoped_session(
            PartialSignallingSession, scopefunc=scopefunc)

    @locked_cached_property
    def preserve_deleted(self):
        return partial(PreserveDeleted, self)

    def make_connector(self, app, bind=None):
        """Creates the connector for a given state and bind."""
        return _EngineConnector(self, app, bind)


_utc = _pytz.utc
db = SQLAlchemy()


__all__ = [
    'db',
    'CRUDMixin',
    'JSONType',
    'MutableList',
    'MutableDict',
    'Model',
    'SurrogatePK',
    'CSTDateTime',
]


# 我可以吐槽这个东西毛用没有么?
class CRUDMixin(object):
    """
    Mixin that adds convenience methods for
    CRUD (create, read, update, delete) operations.
    """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        if commit:
            db.session.commit()
        return self


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""
    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class.
    """
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):
        if any(
            (isinstance(id, basestring) and id.isdigit(),
             isinstance(id, (int, float))),
        ):
            return cls.query.get(int(id))
        return None


class CSTDateTime(TypeDecorator):
    '''China Standed Time(+08:00)'''

    impl = DateTime

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime):
            value = cst.normalize(value)
        if isinstance(value, basestring):
            value = cst.parse(value)

        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        return cst.normalize(value)


class JSONType(TypeDecorator):

    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class MutableList(Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain list to MutableList."""

        if not isinstance(value, MutableList):
            if isinstance(value, (list, tuple)):
                return MutableList(value)

            # this call will raise ValueError
            return super(MutableList, cls).coerce(key, value)
        else:
            return value

    def __delitem__(self, key):
        rv = super(MutableList, self).__delitem__(key)
        self.changed()
        return rv

    def __delslice__(self, key):
        rv = super(MutableList, self).__delslice__(key)
        self.changed()
        return rv

    def __iadd__(self, other):
        rv = super(MutableList, self).__iadd__(other)
        self.changed()
        return rv

    def __imul__(self, other):
        rv = super(MutableList, self).__imul__(other)
        self.changed()
        return rv

    def __setitem__(self, key, value):
        rv = super(MutableList, self).__setitem__(key, value)
        self.changed()
        return rv

    def __setslice__(self, i, j, value):
        rv = super(MutableList, self).__setslice__(i, j, value)
        self.changed()
        return rv

    def append(self, item):
        rv = super(MutableList, self).append(item)
        self.changed()
        return rv

    def remove(self, item):
        rv = super(MutableList, self).remove(item)
        self.changed()
        return rv

    def extend(self, iterable):
        rv = super(MutableList, self).extend(iterable)
        self.changed()
        return rv

    def insert(self, pos, value):
        rv = super(MutableList, self).insert(pos, value)
        self.changed()
        return rv

    def pop(self, index=-1):
        rv = super(MutableList, self).pop(index)
        self.changed()
        return rv

    def reverse(self):
        rv = super(MutableList, self).reverse()
        self.changed()
        return rv

    def sort(self, cmp=None, key=None, reverse=None):
        rv = super(MutableList, self).sort(cmp, key, reverse)
        self.changed()
        return rv


_iso8601_parser = _re.compile("""
    ^
    (?P<year> [0-9]{4})(?P<ymdsep>-?)
    (?P<month>[0-9]{2})(?P=ymdsep)
    (?P<day>  [0-9]{2})

    (?: # time part... optional... at least hour must be specified
        (?:T|\s+)
        (?P<hour>[0-9]{2})
        (?:
            # minutes, separated with :, or none, from hours
            (?P<hmssep>[:]?)
            (?P<minute>[0-9]{2})
            (?:
                # same for seconds, separated with :, or none, from hours
                (?P=hmssep)
                (?P<second>[0-9]{2})
            )?
        )?

        # fractions
        (?: [,.] (?P<frac>[0-9]{1,10}))?

        # timezone, Z, +-hh or +-hh:?mm. MUST BE, but complain if not there.
        (
            (?P<tzempty>Z)
        |
            (?P<tzh>[+-][0-9]{2})
            (?: :? # optional separator
                (?P<tzm>[0-9]{2})
            )?
        )?
    )?
    $
    """, _re.X)  # """


class FixedOffset(_tzinfo):
    """Fixed offset in minutes east from UTC. Based on
       the python tutorial and pytz test code."""

    def __init__(self, offset, name):
        """Constructor. Create a new tzinfo object
        with given offset in minutes and name."""
        self.__offset = timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

    def localize(self, dt, is_dst=False):
        """Convert naive time to local time. Copied
        from pytz tzinfo classes"""

        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')

        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        """Correct the timezone information on the
        given datetime. Copied from pytz tzinfo classes."""

        if dt.tzinfo is None:
            raise ValueError('Naive time - no tzinfo set')

        return dt.replace(tzinfo=self)

    def __str__(self):
        return self.__name

    def __repr__(self):
        return '<%s>' % self.__name


_fixed_offset_tzs = {}


def _get_fixed_offset_tz(offsetmins):
    """For internal use only: Returns a tzinfo with
    the given fixed offset. This creates only one instance
    for each offset; the zones are kept in a dictionary"""

    if offsetmins == 0:
        return _utc

    if not offsetmins in _fixed_offset_tzs:
        if offsetmins < 0:
            sign = '-'
            absoff = -offsetmins
        else:
            sign = '+'
            absoff = offsetmins

        name = "UTC%s%02d:%02d" % (
            sign, int(absoff / 60),
            absoff % 60)
        inst = FixedOffset(offsetmins, name)
        _fixed_offset_tzs[offsetmins] = inst

    return _fixed_offset_tzs[offsetmins]


def parseisoformat(timestamp):
    """Internal function for parsing a timestamp in
    ISO 8601 format"""

    timestamp = timestamp.strip()

    m = _iso8601_parser.match(timestamp)
    if not m:
        raise ValueError("Not a proper ISO 8601 timestamp!")

    year = int(m.group('year'))
    month = int(m.group('month'))
    day = int(m.group('day'))

    h, min, s, us = None, None, None, 0
    frac = 0
    if m.group('tzempty') is None and m.group('tzh') is None:
        raise ValueError(
            "Not a proper ISO 8601 timestamp: " +
            "missing timezone (Z or +hh[:mm])!")

    if m.group('frac'):
        frac = m.group('frac')
        power = len(frac)
        frac = long(frac) / 10.0 ** power

    if m.group('hour'):
        h = int(m.group('hour'))

    if m.group('minute'):
        min = int(m.group('minute'))

    if m.group('second'):
        s = int(m.group('second'))

    if frac is not None:
        # ok, fractions of hour?
        if min is None:
            frac, min = _math.modf(frac * 60.0)
            min = int(min)

        # fractions of second?
        if s is None:
            frac, s = _math.modf(frac * 60.0)
            s = int(s)

        # and extract microseconds...
        us = int(frac * 1000000)

    if m.group('tzempty') == 'Z':
        offsetmins = 0
    else:
        # timezone: hour diff with sign
        offsetmins = int(m.group('tzh')) * 60
        tzm = m.group('tzm')

        # add optional minutes
        if tzm is not None:
            tzm = long(tzm)
            offsetmins += tzm if offsetmins > 0 else -tzm

    tz = _get_fixed_offset_tz(offsetmins)
    return datetime(year, month, day, h, min, s, us, tz)
