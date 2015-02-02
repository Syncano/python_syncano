import re
import six
from urlparse import urljoin

from syncano.connection import ConnectionMixin
from syncano.exceptions import SyncanoValueError
from syncano.models.registry import registry
from syncano.utils import camelcase_to_underscore


class Options(ConnectionMixin):

    def __init__(self, meta=None):
        self.name = None
        self.plural_name = None
        self.related_name = None
        self.parent = None

        self.endpoints = {}
        self.endpoint_fields = []

        self.fields = []
        self.field_names = []

        self._pk = False

        if meta:
            meta_attrs = meta.__dict__.copy()
            for name in meta.__dict__:
                if name.startswith('_') or not hasattr(self, name):
                    del meta_attrs[name]

            for name, value in meta_attrs.iteritems():
                setattr(self, name, value)

        for name, endpoint in six.iteritems(self.endpoints):
            if 'properties' not in endpoint:
                properties = self.get_path_properties(endpoint['path'])
                endpoint['properties'] = properties
                self.endpoint_fields.extend((
                    p for p in properties if p not in self.endpoint_fields
                ))

    def contribute_to_class(self, cls, name):
        if not self.name:
            model_name = camelcase_to_underscore(cls.__name__)
            self.name = model_name.replace('_', ' ').capitalize()

        if not self.plural_name:
            self.plural_name = '{0}s'.format(self.name)

        if not self.related_name:
            self.related_name = self.plural_name.replace(' ', '_').lower()

        if self.parent and isinstance(self.parent, six.string_types):
            self.parent = registry.get_model_by_name(self.parent)

        self.resolve_parent_data()

        setattr(cls, name, self)

    def resolve_parent_data(self):
        if not self.parent:
            return

        meta = self.parent._meta
        name = meta.name.replace(' ', '_').lower()
        endpoint = meta.get_endpoint('detail')
        properties = ['{0}_{1}'.format(name, p) for p in endpoint['properties']]
        prefix = endpoint['path']

        for old, new in zip(endpoint['properties'], properties):
            prefix = prefix.replace(old, new)

        for name, endpoint in six.iteritems(self.endpoints):
            endpoint['properties'] = properties + endpoint['properties']
            endpoint['path'] = urljoin(prefix, endpoint['path'].lstrip('/'))

    def add_field(self, field):
        if field.name in self.field_names:
            raise SyncanoValueError('Field "{0}" already defined'.format(field.name))

        self.field_names.append(field.name)
        self.fields.append(field)

    def get_endpoint(self, name):
        if name not in self.endpoints:
            raise SyncanoValueError('Invalid path name: "{0}".'.format(name))
        return self.endpoints[name]

    def get_endpoint_properties(self, name):
        endpoint = self.get_endpoint(name)
        return endpoint['properties']

    def get_endpoint_path(self, name):
        endpoint = self.get_endpoint(name)
        return endpoint['path']

    def resolve_endpoint(self, name, properties):
        endpoint = self.get_endpoint(name)

        for name in endpoint['properties']:
            if name not in properties:
                raise SyncanoValueError('Request property "{0}" is required.'.format(name))

        return endpoint['path'].format(**properties)

    def get_endpoint_query_params(self, name, params):
        properties = self.get_endpoint_properties(name)
        return {k: v for k, v in params.iteritems() if k not in properties}

    def get_path_properties(self, path):
        return re.findall('/{([^}]*)}', path)
