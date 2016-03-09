from __future__ import unicode_literals

import json

from syncano.exceptions import SyncanoValidationError

from . import fields
from .base import Model
from .instances import Instance
from .manager import ScriptEndpointManager, ScriptManager


class Script(Model):
    """
    OO wrapper around scripts `endpoint <http://docs.syncano.com/v4.0/docs/codebox-list-codeboxes>`_.

    :ivar label: :class:`~syncano.models.fields.StringField`
    :ivar description: :class:`~syncano.models.fields.StringField`
    :ivar source: :class:`~syncano.models.fields.StringField`
    :ivar runtime_name: :class:`~syncano.models.fields.ChoiceField`
    :ivar config: :class:`~syncano.models.fields.Field`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`
    :ivar created_at: :class:`~syncano.models.fields.DateTimeField`
    :ivar updated_at: :class:`~syncano.models.fields.DateTimeField`

    .. note::
        **Script** has special method called ``run`` which will execute attached source code::

            >>> Script.please.run('instance-name', 1234)
            >>> Script.please.run('instance-name', 1234, payload={'variable_one': 1, 'variable_two': 2})
            >>> Script.please.run('instance-name', 1234, payload="{\"variable_one\": 1, \"variable_two\": 2}")

        or via instance::

            >>> s = Script.please.get('instance-name', 1234)
            >>> s.run()
            >>> s.run(variable_one=1, variable_two=2)
    """

    RUNTIME_CHOICES = (
        {'display_name': 'nodejs', 'value': 'nodejs'},
        {'display_name': 'python', 'value': 'python'},
        {'display_name': 'ruby', 'value': 'ruby'},
        {'display_name': 'golang', 'value': 'golang'},
    )

    label = fields.StringField(max_length=80)
    description = fields.StringField(required=False)
    source = fields.StringField()
    runtime_name = fields.ChoiceField(choices=RUNTIME_CHOICES)
    config = fields.Field(required=False)
    links = fields.LinksField()
    created_at = fields.DateTimeField(read_only=True, required=False)
    updated_at = fields.DateTimeField(read_only=True, required=False)

    traces = fields.RelatedManagerField('ScriptTrace')

    please = ScriptManager()

    class Meta:
        parent = Instance
        name = 'Script'
        plural_name = 'Scripts'
        endpoints = {
            'detail': {
                'methods': ['put', 'get', 'patch', 'delete'],
                'path': '/snippets/scripts/{id}/',
            },
            'list': {
                'methods': ['post', 'get'],
                'path': '/snippets/scripts/',
            },
            'run': {
                'methods': ['post'],
                'path': '/snippets/scripts/{id}/run/',
            },
        }

    def run(self, **payload):
        """
        Usage::

            >>> s = Script.please.get('instance-name', 1234)
            >>> s.run()
            >>> s.run(variable_one=1, variable_two=2)
        """
        from .traces import ScriptTrace

        if self.is_new():
            raise SyncanoValidationError('Method allowed only on existing model.')

        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('run', properties)
        connection = self._get_connection(**payload)
        request = {
            'data': {
                'payload': json.dumps(payload)
            }
        }
        response = connection.request('POST', endpoint, **request)
        response.update({'instance_name': self.instance_name, 'script_id': self.id})
        return ScriptTrace(**response)


class Schedule(Model):
    """
    OO wrapper around script schedules `endpoint <http://docs.syncano.com/v4.0/docs/codebox-schedules-list>`_.

    :ivar label: :class:`~syncano.models.fields.StringField`
    :ivar script: :class:`~syncano.models.fields.IntegerField`
    :ivar interval_sec: :class:`~syncano.models.fields.IntegerField`
    :ivar crontab: :class:`~syncano.models.fields.StringField`
    :ivar payload: :class:`~syncano.models.fields.HyperliStringFieldnkedField`
    :ivar created_at: :class:`~syncano.models.fields.DateTimeField`
    :ivar scheduled_next: :class:`~syncano.models.fields.DateTimeField`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`
    """

    label = fields.StringField(max_length=80)
    script = fields.IntegerField(label='script id')
    interval_sec = fields.IntegerField(read_only=False, required=False)
    crontab = fields.StringField(max_length=40, required=False)
    payload = fields.StringField(required=False)
    created_at = fields.DateTimeField(read_only=True, required=False)
    scheduled_next = fields.DateTimeField(read_only=True, required=False)
    links = fields.LinksField()

    traces = fields.RelatedManagerField('ScheduleTraces')

    class Meta:
        parent = Instance
        endpoints = {
            'detail': {
                'methods': ['put', 'get', 'patch', 'delete'],
                'path': '/schedules/{id}/',
            },
            'list': {
                'methods': ['post', 'get'],
                'path': '/schedules/',
            }
        }


class Trigger(Model):
    """
    OO wrapper around triggers `endpoint <http://docs.syncano.com/v4.0/docs/triggers-list>`_.

    :ivar label: :class:`~syncano.models.fields.StringField`
    :ivar script: :class:`~syncano.models.fields.IntegerField`
    :ivar class_name: :class:`~syncano.models.fields.StringField`
    :ivar signal: :class:`~syncano.models.fields.ChoiceField`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`
    :ivar created_at: :class:`~syncano.models.fields.DateTimeField`
    :ivar updated_at: :class:`~syncano.models.fields.DateTimeField`
    """

    SIGNAL_CHOICES = (
        {'display_name': 'post_update', 'value': 'post_update'},
        {'display_name': 'post_create', 'value': 'post_create'},
        {'display_name': 'post_delete', 'value': 'post_delete'},
    )

    label = fields.StringField(max_length=80)
    script = fields.IntegerField(label='script id')
    class_name = fields.StringField(label='class name', mapping='class')
    signal = fields.ChoiceField(choices=SIGNAL_CHOICES)
    links = fields.LinksField()
    created_at = fields.DateTimeField(read_only=True, required=False)
    updated_at = fields.DateTimeField(read_only=True, required=False)

    traces = fields.RelatedManagerField('TriggerTrace')

    class Meta:
        parent = Instance
        endpoints = {
            'detail': {
                'methods': ['put', 'get', 'patch', 'delete'],
                'path': '/triggers/{id}/',
            },
            'list': {
                'methods': ['post', 'get'],
                'path': '/triggers/',
            }
        }


class ScriptEndpoint(Model):
    # TODO: update docs when ready;
    """
    OO wrapper around script endpoints `endpoint <http://docs.syncano.com/v4.0/docs/webhooks-list>`_.

    :ivar name: :class:`~syncano.models.fields.SlugField`
    :ivar script: :class:`~syncano.models.fields.IntegerField`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`

    .. note::
        **ScriptEndpoint** has special method called ``run`` which will execute related script::

            >>> ScriptEndpoint.please.run('instance-name', 'script-name')
            >>> ScriptEndpoint.please.run('instance-name', 'script-name', payload={'variable_one': 1,
                                                                                   'variable_two': 2})
            >>> ScriptEndpoint.please.run('instance-name', 'script-name',
                                   payload="{\"variable_one\": 1, \"variable_two\": 2}")

        or via instance::

            >>> se = ScriptEndpoint.please.get('instance-name', 'script-name')
            >>> se.run()
            >>> se.run(variable_one=1, variable_two=2)

    """

    name = fields.SlugField(max_length=50, primary_key=True)
    script = fields.IntegerField(label='script id')
    public = fields.BooleanField(required=False, default=False)
    public_link = fields.ChoiceField(required=False, read_only=True)
    links = fields.LinksField()

    traces = fields.RelatedManagerField('ScriptEndpointTrace')
    please = ScriptEndpointManager()

    class Meta:
        parent = Instance
        endpoints = {
            'detail': {
                'methods': ['put', 'get', 'patch', 'delete'],
                'path': '/endpoints/scripts/{name}/',
            },
            'list': {
                'methods': ['post', 'get'],
                'path': '/endpoints/scripts/',
            },
            'run': {
                'methods': ['post'],
                'path': '/endpoints/scripts/{name}/run/',
            },
            'reset': {
                'methods': ['post'],
                'path': '/endpoints/scripts/{name}/reset_link/',
            },
            'public': {
                'methods': ['get'],
                'path': '/endpoints/scripts/p/{public_link}/{name}/',
            }
        }

    def run(self, **payload):
        """
        Usage::

            >>> se = ScriptEndpoint.please.get('instance-name', 'script-name')
            >>> se.run()
            >>> se.run(variable_one=1, variable_two=2)
        """
        from .traces import ScriptEndpointTrace

        if self.is_new():
            raise SyncanoValidationError('Method allowed only on existing model.')

        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('run', properties)
        connection = self._get_connection(**payload)

        response = connection.request('POST', endpoint, **{'data': payload})
        if 'result' in response and 'stdout' in response['result']:
            response.update({'instance_name': self.instance_name,
                             'script_name': self.name})
            return ScriptEndpointTrace(**response)
        # if script is a custom one, return result 'as-it-is';
        return response

    def reset_link(self):
        """
        Usage::

            >>> se = ScriptEndpoint.please.get('instance-name', 'script-name')
            >>> se.reset_link()
        """
        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('reset', properties)
        connection = self._get_connection()

        response = connection.request('POST', endpoint)
        self.public_link = response['public_link']


class ResponseTemplate(Model):
    """
    OO wrapper around templates.

    :ivar name: :class:`~syncano.models.fields.StringField`
    :ivar content: :class:`~syncano.models.fields.StringField`
    :ivar content_type: :class:`~syncano.models.fields.StringField`
    :ivar context: :class:`~syncano.models.fields.JSONField`
    :ivar links: :class:`~syncano.models.fields.HyperlinkedField`
    :ivar created_at: :class:`~syncano.models.fields.DateTimeField`
    :ivar updated_at: :class:`~syncano.models.fields.DateTimeField`
    """

    name = fields.StringField(max_length=64)
    content = fields.StringField(label='content')
    content_type = fields.StringField(label='content type')
    context = fields.JSONField(label='context')
    links = fields.LinksField()

    created_at = fields.DateTimeField(read_only=True, required=False)
    updated_at = fields.DateTimeField(read_only=True, required=False)

    class Meta:
        parent = Instance
        endpoints = {
            'detail': {
                'methods': ['put', 'get', 'patch', 'delete'],
                'path': '/snippets/templates/{name}/',
            },
            'list': {
                'methods': ['post', 'get'],
                'path': '/snippets/templates/',
            },
            'render': {
                'methods': ['post'],
                'path': '/snippets/templates/{name}/render/',
            },
        }

    def render(self, context=None):
        context = context or {}
        properties = self.get_endpoint_data()
        endpoint = self._meta.resolve_endpoint('render', properties)

        connection = self._get_connection()
        return connection.request('POST', endpoint, data={'context': context})
