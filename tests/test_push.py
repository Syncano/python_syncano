# -*- coding: utf-8 -*-
import json
import unittest
from datetime import datetime

from mock import mock
from syncano.models import APNSDevice, APNSMessage, GCMDevice, GCMMessage


class ScriptTestCase(unittest.TestCase):

    @mock.patch('syncano.models.GCMDevice._get_connection')
    def test_gcm_device(self, connection_mock):
        model = GCMDevice(
            instance_name='test',
            label='example label',
            registration_id=86152312314401555,
            device_id='10000000001',
        )

        connection_mock.return_value = connection_mock
        connection_mock.request.return_value = {'registration_id': 86152312314401555}

        self.assertFalse(connection_mock.called)
        self.assertFalse(connection_mock.request.called)

        model.save()

        self.assertTrue(connection_mock.called)
        self.assertTrue(connection_mock.request.called)

        connection_mock.assert_called_once_with()
        connection_mock.request.assert_called_once_with(
            'POST', '/v1.1/instances/test/push_notifications/gcm/devices/',
            data={"registration_id": '86152312314401555', "device_id": "10000000001", "is_active": True,
                  "label": "example label"}
        )
        model.created_at = datetime.now()  # to Falsify is_new()
        model.delete()
        connection_mock.request.assert_called_with(
            'DELETE', '/v1.1/instances/test/push_notifications/gcm/devices/86152312314401555/'
        )

    @mock.patch('syncano.models.APNSDevice._get_connection')
    def test_apns_device(self, connection_mock):
        # just mock test - values here should be different;
        model = APNSDevice(
            instance_name='test',
            label='example label',
            registration_id=86152312314401555,
            device_id='10000000001',
        )

        connection_mock.return_value = connection_mock
        connection_mock.request.return_value = {'registration_id': 86152312314401555}

        self.assertFalse(connection_mock.called)
        self.assertFalse(connection_mock.request.called)

        model.save()

        self.assertTrue(connection_mock.called)
        self.assertTrue(connection_mock.request.called)

        connection_mock.assert_called_once_with()
        connection_mock.request.assert_called_once_with(
            'POST', '/v1.1/instances/test/push_notifications/apns/devices/',
            data={"registration_id": '86152312314401555', "device_id": "10000000001", "is_active": True,
                  "label": "example label"}
        )

        model.created_at = datetime.now()  # to Falsify is_new()
        model.delete()
        connection_mock.request.assert_called_with(
            'DELETE', '/v1.1/instances/test/push_notifications/apns/devices/86152312314401555/'
        )

    @mock.patch('syncano.models.GCMMessage._get_connection')
    def test_gcm_message(self, connection_mock):
        model = GCMMessage(
            instance_name='test',
            content={'data': 'some data'}
        )
        connection_mock.return_value = connection_mock

        self.assertFalse(connection_mock.called)
        self.assertFalse(connection_mock.request.called)

        model.save()

        self.assertTrue(connection_mock.called)
        self.assertTrue(connection_mock.request.called)

        connection_mock.assert_called_once_with()

        call_args = connection_mock.request.call_args[0]
        call_kwargs = connection_mock.request.call_args[1]

        call_kwargs['data']['content'] = json.loads(call_kwargs['data']['content'])

        self.assertEqual(('POST', '/v1.1/instances/test/push_notifications/gcm/messages/'), call_args)
        self.assertDictEqual(
            {'data': {'content': {"environment": "production", "data": "some data"}}},
            call_kwargs,
        )

    @mock.patch('syncano.models.APNSMessage._get_connection')
    def test_apns_message(self, connection_mock):
        model = APNSMessage(
            instance_name='test',
            content={'data': 'some data'}
        )
        connection_mock.return_value = connection_mock

        self.assertFalse(connection_mock.called)
        self.assertFalse(connection_mock.request.called)

        model.save()

        self.assertTrue(connection_mock.called)
        self.assertTrue(connection_mock.request.called)

        connection_mock.assert_called_once_with()
        call_args = connection_mock.request.call_args[0]
        call_kwargs = connection_mock.request.call_args[1]
        call_kwargs['data']['content'] = json.loads(call_kwargs['data']['content'])
        self.assertEqual(('POST', '/v1.1/instances/test/push_notifications/apns/messages/'), call_args)
        self.assertDictEqual(call_kwargs['data'], {'content': {"environment": "production", "data": "some data"}})
