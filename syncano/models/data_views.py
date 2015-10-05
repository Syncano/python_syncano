from __future__ import unicode_literals

from . import fields
from .base import Model
from .instances import Instance


class DataView(Model):
    """
    :ivar name: :class:`~syncano.models.fields.StringField`
    :ivar description: :class:`~syncano.models.fields.StringField`
    :ivar query: :class:`~syncano.models.fields.SchemaField`
    :ivar class_name: :class:`~syncano.models.fields.StringField`
    :ivar excluded_fields: :class:`~syncano.models.fields.StringField`
    :ivar expand: :class:`~syncano.models.fields.StringField`
    :ivar order_by: :class:`~syncano.models.fields.StringField`
    :ivar page_size: :class:`~syncano.models.fields.IntegerField`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`
    """

    LINKS = [
        {'type': 'detail', 'name': 'self'},
        {'type': 'list', 'name': 'data_views'},
    ]

    PERMISSIONS_CHOICES = (
        {'display_name': 'None', 'value': 'none'},
        {'display_name': 'Read', 'value': 'read'},
        {'display_name': 'Write', 'value': 'write'},
        {'display_name': 'Full', 'value': 'full'},
    )

    name = fields.StringField(max_length=64, primary_key=True)
    description = fields.StringField(required=False)

    query = fields.SchemaField(read_only=False, required=True)

    class_name = fields.StringField(label='class name', mapping='class')

    excluded_fields = fields.StringField(required=False)
    expand = fields.StringField(required=False)
    order_by = fields.StringField(required=False)
    page_size = fields.IntegerField(required=False)

    links = fields.HyperlinkedField(links=LINKS)

    class Meta:
        parent = Instance
        plural_name = 'DataViews'
        endpoints = {
            'detail': {
                'methods': ['get', 'put', 'patch', 'delete'],
                'path': '/api/objects/{name}/',
            },
            'list': {
                'methods': ['post', 'get'],
                'path': '/api/objects/',
            },
            'get_api': {
                'methods': ['get'],
                'path': '/api/objects/{name}/get_api/',
            },
            'rename': {
                'methods': ['post'],
                'path': '/api/objects/{name}/rename/',
            },
            'clear_cache': {
                'methods': ['post'],
                'path': '/api/objects/{name}/clear_cache/',
            }
        }

    def rename(self, new_name):
        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('rename', properties)
        connection = self._get_connection()
        return connection.request('POST',
                                  endpoint,
                                  data={'new_name': new_name})

    def clear_cache(self):
        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('clear_cache', properties)
        connection = self._get_connection()
        return connection.request('POST', endpoint)

    def get_api(self):
        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('get_api', properties)
        connection = self._get_connection()
        while endpoint is not None:
            response = connection.request('GET', endpoint)
            endpoint = response.get('next')
            for obj in response['objects']:
                yield obj
