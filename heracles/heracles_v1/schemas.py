# -*- coding: utf-8 -*-

# TODO: datetime support

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###


DefinitionsBlog = {'type': 'object', 'properties': {'is_published': {'type': 'boolean'}, 'category_id': {'type': 'integer'}, 'title': {'type': 'string'}, 'date_created': {'type': 'string', 'format': 'date-time'}, 'date_modified': {'type': 'string', 'format': 'date-time'}, 'id': {'type': 'integer'}, 'summary': {'type': 'string'}}}
DefinitionsTag = {'type': 'object', 'properties': {'date_created': {'type': 'string', 'format': 'date-time'}, 'title': {'type': 'string'}, 'id': {'type': 'integer'}, 'summary': {'type': 'string'}}}
DefinitionsCategory = {'type': 'object', 'properties': {'date_created': {'type': 'string', 'format': 'date-time'}, 'title': {'type': 'string'}, 'id': {'type': 'integer'}, 'summary': {'type': 'string'}}}
DefinitionsError = {'type': 'object', 'properties': {'fields': {'type': 'string'}, 'message': {'type': 'string'}, 'code': {'type': 'integer', 'format': 'int32'}}}

validators = {
    ('categorys', 'POST'): {'json': DefinitionsCategory},
    ('categorys', 'GET'): {'args': {'required': [], 'properties': {'limit': {'description': 'max records to return', 'format': 'int32', 'default': 20, 'maximum': 1000, 'minimum': 1, 'type': 'integer'}, 'page': {'description': 'page number', 'format': 'int32', 'default': 1, 'maximum': 1000, 'minimum': 0, 'type': 'integer'}}}},
    ('blog_blog_id', 'PUT'): {'json': DefinitionsBlog},
    ('category_category_id', 'PUT'): {'json': DefinitionsCategory},
    ('tag_tag_id', 'PUT'): {'json': DefinitionsTag},
    ('blogs', 'POST'): {'json': DefinitionsBlog},
    ('blogs', 'GET'): {'args': {'required': [], 'properties': {'limit': {'description': 'max records to return', 'format': 'int32', 'default': 20, 'maximum': 1000, 'minimum': 1, 'type': 'integer'}, 'page': {'description': 'page number', 'format': 'int32', 'default': 1, 'maximum': 1000, 'minimum': 0, 'type': 'integer'}}}},
    ('tags', 'POST'): {'json': DefinitionsTag},
    ('tags', 'GET'): {'args': {'required': [], 'properties': {'limit': {'description': 'max records to return', 'format': 'int32', 'default': 20, 'maximum': 1000, 'minimum': 1, 'type': 'integer'}, 'page': {'description': 'page number', 'format': 'int32', 'default': 1, 'maximum': 1000, 'minimum': 0, 'type': 'integer'}}}},
}

filters = {
    ('categorys', 'POST'): {201: {'headers': None, 'schema': DefinitionsCategory}},
    ('categorys', 'GET'): {200: {'headers': None, 'schema': {'items': DefinitionsCategory, 'type': 'array'}}},
    ('blog_blog_id', 'PUT'): {201: {'headers': None, 'schema': None}},
    ('blog_blog_id', 'GET'): {200: {'headers': None, 'schema': DefinitionsBlog}},
    ('blog_blog_id', 'DELETE'): {200: {'headers': None, 'schema': None}},
    ('category_category_id', 'PUT'): {201: {'headers': None, 'schema': None}},
    ('category_category_id', 'GET'): {200: {'headers': None, 'schema': DefinitionsCategory}},
    ('category_category_id', 'DELETE'): {200: {'headers': None, 'schema': None}},
    ('tag_tag_id', 'PUT'): {201: {'headers': None, 'schema': None}},
    ('tag_tag_id', 'GET'): {200: {'headers': None, 'schema': DefinitionsTag}},
    ('tag_tag_id', 'DELETE'): {200: {'headers': None, 'schema': None}},
    ('blogs', 'POST'): {201: {'headers': None, 'schema': DefinitionsBlog}},
    ('blogs', 'GET'): {200: {'headers': None, 'schema': {'items': DefinitionsBlog, 'type': 'array'}}},
    ('tags', 'POST'): {201: {'headers': None, 'schema': DefinitionsTag}},
    ('tags', 'GET'): {200: {'headers': None, 'schema': {'items': DefinitionsTag, 'type': 'array'}}},
}

scopes = {
}


class Security(object):

    def __init__(self):
        super(Security, self).__init__()
        self._loader = lambda: []

    @property
    def scopes(self):
        return self._loader()

    def scopes_loader(self, func):
        self._loader = func
        return func

security = Security()


def merge_default(schema, value):
    # TODO: more types support
    type_defaults = {
        'integer': 9573,
        'string': 'something',
        'object': {},
        'array': [],
        'boolean': False
    }

    return normalize(schema, value, type_defaults)[0]


def normalize(schema, data, required_defaults=None):

    if required_defaults is None:
        required_defaults = {}
    errors = []

    class DataWrapper(object):

        def __init__(self, data):
            super(DataWrapper, self).__init__()
            self.data = data

        def get(self, key, default=None):
            if isinstance(self.data, dict):
                return self.data.get(key, default)
            if hasattr(self.data, key):
                return getattr(self.data, key)
            else:
                return default

        def has(self, key):
            if isinstance(self.data, dict):
                return key in self.data
            return hasattr(self.data, key)

    def _normalize_dict(schema, data):
        result = {}
        data = DataWrapper(data)
        for key, _schema in schema.get('properties', {}).iteritems():
            # set default
            type_ = _schema.get('type', 'object')
            if ('default' not in _schema
                    and key in schema.get('required', [])
                    and type_ in required_defaults):
                _schema['default'] = required_defaults[type_]

            # get value
            if data.has(key):
                result[key] = _normalize(_schema, data.get(key))
            elif 'default' in _schema:
                result[key] = _schema['default']
            elif key in schema.get('required', []):
                errors.append(dict(name='property_missing',
                                   message='`%s` is required' % key))
        return result

    def _normalize_list(schema, data):
        result = []
        if hasattr(data, '__iter__') and not isinstance(data, dict):
            for item in data:
                result.append(_normalize(schema.get('items'), item))
        elif 'default' in schema:
            result = schema['default']
        return result

    def _normalize_default(schema, data):
        if data is None:
            return schema.get('default')
        else:
            return data

    def _normalize(schema, data):
        if not schema:
            return None
        funcs = {
            'object': _normalize_dict,
            'array': _normalize_list,
            'default': _normalize_default,
        }
        type_ = schema.get('type', 'object')
        if not type_ in funcs:
            type_ = 'default'

        return funcs[type_](schema, data)

    return _normalize(schema, data), errors

