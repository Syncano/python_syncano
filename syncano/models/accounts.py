from __future__ import unicode_literals

from . import fields
from .base import Model
from .instances import Instance


class Admin(Model):
    """
    OO wrapper around instance admins `endpoint <http://docs.syncano.com/v4.0/docs/v1instancesinstanceadmins>`_.

    :ivar first_name: :class:`~syncano.models.fields.StringField`
    :ivar last_name: :class:`~syncano.models.fields.StringField`
    :ivar email: :class:`~syncano.models.fields.EmailField`
    :ivar role: :class:`~syncano.models.fields.ChoiceField`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`
    """
    LINKS = (
        {'type': 'detail', 'name': 'self'},
    )
    ROLE_CHOICES = (
        {'display_name': 'full', 'value': 'full'},
        {'display_name': 'write', 'value': 'write'},
        {'display_name': 'read', 'value': 'read'},
    )

    first_name = fields.StringField(read_only=True, required=False)
    last_name = fields.StringField(read_only=True, required=False)
    email = fields.EmailField(read_only=True, required=False)
    role = fields.ChoiceField(choices=ROLE_CHOICES)
    links = fields.HyperlinkedField(links=LINKS)

    class Meta:
        parent = Instance
        endpoints = {
            'detail': {
                'methods': ['put', 'get', 'patch', 'delete'],
                'path': '/admins/{id}/',
            },
            'list': {
                'methods': ['get'],
                'path': '/admins/',
            }
        }


class Profile(Model):
    """
    """
    LINKS = (
        {'type': 'detail', 'name': 'self'},
    )

    PERMISSIONS_CHOICES = (
        {'display_name': 'None', 'value': 'none'},
        {'display_name': 'Read', 'value': 'read'},
        {'display_name': 'Create users', 'value': 'create_users'},
    )

    owner = fields.IntegerField(label='owner id', required=False, read_only=True)
    owner_permissions = fields.ChoiceField(choices=PERMISSIONS_CHOICES, default='none')
    group = fields.IntegerField(label='group id', required=False)
    group_permissions = fields.ChoiceField(choices=PERMISSIONS_CHOICES, default='none')
    other_permissions = fields.ChoiceField(choices=PERMISSIONS_CHOICES, default='none')
    channel = fields.StringField(required=False)
    channel_room = fields.StringField(required=False, max_length=64)

    schema = fields.SchemaField(read_only=False, required=True)

    links = fields.HyperlinkedField(links=LINKS)
    created_at = fields.DateTimeField(read_only=True, required=False)
    updated_at = fields.DateTimeField(read_only=True, required=False)

    class Meta:
        parent = Instance
        endpoints = {
            'detail': {
                'methods': ['delete', 'patch', 'put', 'get'],
                'path': '/users/{id}/',
            },
            'reset_key': {
                'methods': ['post'],
                'path': '/users/{id}/reset_key/',
            },
            'list': {
                'methods': ['get'],
                'path': '/users/',
            }
        }


class User(Model):
    """
    OO wrapper around users `endpoint <http://docs.syncano.com/v4.0/docs/user-management>`_.

    :ivar username: :class:`~syncano.models.fields.StringField`
    :ivar password: :class:`~syncano.models.fields.StringField`
    :ivar user_key: :class:`~syncano.models.fields.StringField`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`
    :ivar created_at: :class:`~syncano.models.fields.DateTimeField`
    :ivar updated_at: :class:`~syncano.models.fields.DateTimeField`
    """
    LINKS = (
        {'type': 'detail', 'name': 'self'},
    )

    username = fields.StringField(max_length=64, required=True)
    password = fields.StringField(read_only=False, required=True)
    user_key = fields.StringField(read_only=True, required=False)

    profile = fields.ModelField('Profile')

    links = fields.HyperlinkedField(links=LINKS)
    created_at = fields.DateTimeField(read_only=True, required=False)
    updated_at = fields.DateTimeField(read_only=True, required=False)

    class Meta:
        parent = Instance
        endpoints = {
            'detail': {
                'methods': ['delete', 'patch', 'put', 'get'],
                'path': '/users/{id}/',
            },
            'reset_key': {
                'methods': ['post'],
                'path': '/users/{id}/reset_key/',
            },
            'list': {
                'methods': ['get'],
                'path': '/users/',
            }
        }

    def reset_key(self):
        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('reset_key', properties)
        connection = self._get_connection()
        return connection.request('POST', endpoint)


class Group(Model):
    """
    OO wrapper around users `endpoint <http://docs.syncano.com/v4.0/docs/groups>`_.

    :ivar label: :class:`~syncano.models.fields.StringField`
    :ivar description: :class:`~syncano.models.fields.StringField`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`
    :ivar created_at: :class:`~syncano.models.fields.DateTimeField`
    :ivar updated_at: :class:`~syncano.models.fields.DateTimeField`
    """
    LINKS = (
        {'type': 'detail', 'name': 'self'},
    )

    label = fields.StringField(max_length=64, required=True)
    description = fields.StringField(read_only=False, required=False)

    links = fields.HyperlinkedField(links=LINKS)
    created_at = fields.DateTimeField(read_only=True, required=False)
    updated_at = fields.DateTimeField(read_only=True, required=False)

    class Meta:
        parent = Instance
        endpoints = {
            'detail': {
                'methods': ['delete', 'patch', 'put', 'get'],
                'path': '/groups/{id}/',
            },
            'list': {
                'methods': ['get'],
                'path': '/groups/',
            },
            'users': {
                'methods': ['get', 'post', 'delete'],
                'path': '/groups/{id}/users/',
            }
        }

    def group_users_method(self, user_id=None, method='GET'):
        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('reset_key', properties)
        if user_id is not None:
            endpoint += '{}/'.format(user_id)
        connection = self._get_connection()
        return connection.request(method, endpoint)

    def list_users(self):
        return self.group_users_method()

    def add_user(self, user_id):
        return self.group_users_method(user_id, method='POST')

    def get_user_details(self, user_id):
        return self.group_users_method(user_id)

    def delete_user(self, user_id):
        return self.group_users_method(user_id, method='DELETE')
