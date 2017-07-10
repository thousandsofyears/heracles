import re
from datetime import tzinfo, timedelta, datetime
import unittest

rfc3339_regex = (
    r'^(?P<year>\d{4})-?(?P<month>\d{2})-?(?P<day>\d{2})'
    r'T'
    r'(?P<hour>\d{2}):?(?P<minute>\d{2}):?(?P<second>\d{2})(\.(?P<microsecond>\d{1,6}))?'
    r'((?P<tz_utc>Z)|(?P<tz_sign>[\+\-])(?P<tz_hour>\d{2})(:(?P<tz_minute>\d{2}))?)$'
)


def strptime(date_string, tzinfo=None):
    m = re.match(rfc3339_regex, date_string)
    if not m:
        raise ValueError('`%s` is not a rfc3339 format.' % date_string)
    delta = timedelta(0)
    if not m.group('tz_utc'):
        sign = -1 if m.group('tz_sign') == '-' else 1
        hours = int(m.group('tz_hour')) * sign
        minutes = int(m.group('tz_minute') or 0) * sign
        delta = timedelta(hours=hours, minutes=minutes)
    params = dict(
        year=int(m.group('year')),
        month=int(m.group('month')),
        day=int(m.group('day')),
        hour=int(m.group('hour')),
        minute=int(m.group('minute')),
        second=int(m.group('second')),
        tzinfo=Timezone(delta)
    )
    if m.group('microsecond'):
        params['microsecond'] = int(m.group('microsecond'))
    dt = datetime(**params)
    if tzinfo:
        return tzinfo.normalize(dt)
    return dt


class Timezone(tzinfo):

    _offset = timedelta(0)
    _tzname = ''

    def __init__(self, delta=None):
        super(Timezone, self).__init__()
        self._offset = delta or self._offset
        self._tzname = str(self._offset)

    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        return self._tzname

    def dst(self, dt):
        return timedelta(0)

    def normalize(self, dt):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self)
        return dt.astimezone(self)

    def strptime(self, date_string):
        return self.parse(date_string)

    def parse(self, date_string):
        return strptime(date_string, self)

    def datetime(self, *args):
        return datetime(*args, tzinfo=self)

    def now(self):
        return self.normalize(datetime.utcnow())

    def __cmp__(self, other):
        return cmp(self._offset, other._offset)

    def __repr__(self):
        return "<Timezone %s>" % self._tzname


class UTC(Timezone):
    """UTC Timezone"""

    _offset = timedelta(0)
    _tzname = 'UTC'


class CST(Timezone):
    '''China Standard Time'''

    _offset = timedelta(hours=8)
    _tzname = 'CST'

utc = UTC()
cst = CST()


def now():
    return cst.normalize(datetime.now())


class TestCase(unittest.TestCase):

    def test_timezone_normalize(self):
        dt = datetime(2015, 7, 13)

        dt_utc = utc.normalize(dt)
        self.assertEquals(dt_utc.tzinfo, utc)
        self.assertEquals(dt_utc.isoformat(), '2015-07-13T00:00:00+00:00')

        dt_cst = cst.normalize(dt)
        self.assertEquals(dt_cst.tzinfo, cst)
        self.assertEquals(dt_cst.isoformat(), '2015-07-13T00:00:00+08:00')

        dt_utc_plus_8 = cst.normalize(dt_utc)
        self.assertEquals(dt_utc_plus_8.tzinfo, cst)
        self.assertEquals(dt_utc_plus_8.isoformat(), '2015-07-13T08:00:00+08:00')

    def test_parse(self):
        cst_cases = [
            ('2015-07-13T08:09:10+08:00', datetime(2015, 7, 13, 8, 9, 10, tzinfo=cst)),
            ('2015-07-13T08:09:10+00:00', datetime(2015, 7, 13, 16, 9, 10, tzinfo=cst)),
            ('2015-07-13T08:09:10Z', datetime(2015, 7, 13, 16, 9, 10, tzinfo=cst)),
            ('2015-07-13T08:09:10-08:00', datetime(2015, 7, 14, 0, 9, 10, tzinfo=cst)),
            ('2015-07-13T08:09:10-08', datetime(2015, 7, 14, 0, 9, 10, tzinfo=cst)),
            ('2015-07-13T08:10:10+08:10', datetime(2015, 7, 13, 8, 0, 10, tzinfo=cst)),
            ('2015-07-13T08:10:10-08:10', datetime(2015, 7, 14, 0, 20, 10, tzinfo=cst)),
        ]
        for string, dt in cst_cases:
            self.assertEquals(
                cst.parse(string),
                dt
            )


if __name__ == '__main__':
    unittest.main()
