# -*- coding: utf-8 -*-

# TODO: datetime support

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

base_path = '/v1'


DefinitionsBlogresponse = {'type': 'object', 'properties': {'content': {'type': 'string'}, 'date_modified': {'type': 'string', 'format': 'date-time'}, 'date_created': {'type': 'string', 'format': 'date-time'}, 'title': {'type': 'string'}, 'id': {'type': 'integer'}, 'is_published': {'type': 'boolean'}}}
DefinitionsBlogrequest = {'type': 'object', 'properties': {'content': {'type': 'string'}, 'title': {'type': 'string'}}}
DefinitionsErrorfield = {'type': 'object', 'properties': {'message': {'type': 'string'}, 'code': {'type': 'string'}, 'filed': {'type': 'string'}}}
DefinitionsError = {'type': 'object', 'properties': {'status': {'type': 'integer'}, 'message': {'default': '', 'type': 'string'}, 'errors': {'default': [], 'items': DefinitionsErrorfield, 'type': 'array'}, 'error_code': {'default': '', 'type': 'string'}}}

validators = {
    ('blog_blog_id', 'PUT'): {'json': DefinitionsBlogrequest},
    ('blogs', 'POST'): {'json': DefinitionsBlogrequest},
    ('blogs', 'GET'): {'args': {'required': [], 'properties': {'limit': {'description': 'max records to return', 'format': 'int32', 'default': 20, 'maximum': 1000, 'minimum': 1, 'type': 'integer'}, 'page': {'description': 'page number', 'format': 'int32', 'default': 1, 'maximum': 1000, 'minimum': 0, 'type': 'integer'}}}},
}

filters = {
    ('blog_blog_id', 'PUT'): {201: {'headers': None, 'schema': None}},
    ('blog_blog_id', 'GET'): {200: {'headers': None, 'schema': DefinitionsBlogresponse}},
    ('blog_blog_id', 'DELETE'): {200: {'headers': None, 'schema': None}},
    ('blogs', 'POST'): {201: {'headers': None, 'schema': DefinitionsBlogresponse}},
    ('blogs', 'GET'): {200: {'headers': None, 'schema': {'items': DefinitionsBlogresponse, 'type': 'array'}}},
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


def merge_default(schema, value, get_first=True):
    # TODO: more types support
    type_defaults = {
        'integer': 9573,
        'string': 'something',
        'object': {},
        'array': [],
        'boolean': False
    }

    results = normalize(schema, value, type_defaults)
    if get_first:
        return results[0]
    return results


def normalize(schema, data, required_defaults=None):

    import six

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
            return getattr(self.data, key, default)

        def has(self, key):
            if isinstance(self.data, dict):
                return key in self.data
            return hasattr(self.data, key)

        def keys(self):
            if isinstance(self.data, dict):
                return list(self.data.keys())
            return list(vars(self.data).keys())

        def get_check(self, key, default=None):
            if isinstance(self.data, dict):
                value = self.data.get(key, default)
                has_key = key in self.data
            else:
                try:
                    value = getattr(self.data, key)
                except AttributeError:
                    value = default
                    has_key = False
                else:
                    has_key = True
            return value, has_key

    def _normalize_dict(schema, data):
        result = {}
        if not isinstance(data, DataWrapper):
            data = DataWrapper(data)

        for key, _schema in six.iteritems(schema.get('properties', {})):
            # set default
            type_ = _schema.get('type', 'object')

            # get value
            value, has_key = data.get_check(key)
            if has_key:
                result[key] = _normalize(_schema, value)
            elif 'default' in _schema:
                result[key] = _schema['default']
            elif key in schema.get('required', []):
                if type_ in required_defaults:
                    result[key] = required_defaults[type_]
                else:
                    errors.append(dict(name='property_missing',
                                       message='`%s` is required' % key))

        for _schema in schema.get('allOf', []):
            rs_component = _normalize(_schema, data)
            rs_component.update(result)
            result = rs_component

        additional_properties_schema = schema.get('additionalProperties', False)
        if additional_properties_schema:
            aproperties_set = set(data.keys()) - set(result.keys())
            for pro in aproperties_set:
                result[pro] = _normalize(additional_properties_schema, data.get(pro))

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

