import logging
import os

__title__ = 'Syncano Python'
__version__ = '4.0.5'
__author__ = 'Daniel Kopka'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Syncano'

env_loglevel = os.getenv('SYNCANO_LOGLEVEL', 'INFO')
loglevel = getattr(logging, env_loglevel.upper(), None)

if not isinstance(loglevel, int):
    raise ValueError('Invalid log level: {0}.'.format(loglevel))

console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

logger = logging.getLogger('syncano')
logger.setLevel(loglevel)
logger.addHandler(console_handler)

# Few global env variables
VERSION = __version__
DEBUG = env_loglevel.lower() == 'debug'
API_ROOT = os.getenv('SYNCANO_APIROOT', 'https://api.syncano.io/')
EMAIL = os.getenv('SYNCANO_EMAIL')
PASSWORD = os.getenv('SYNCANO_PASSWORD')
APIKEY = os.getenv('SYNCANO_APIKEY')
INSTANCE = os.getenv('SYNCANO_INSTANCE')


def connect(*args, **kwargs):
    """
    Connects to Syncano API.

    :type email: string
    :param email: Your Syncano account email address

    :type password: string
    :param password: Your Syncano password

    :type api_key: string
    :param api_key: Your Syncano account key or instance api_key

    :type username: string
    :param username: Your Syncano username

    :type instance_name: string
    :param instance_name: Your Syncano instance_name

    :type verify_ssl: boolean
    :param verify_ssl: Verify SSL certificate

    :rtype: :class:`syncano.models.registry.Registry`
    :return: A models registry

    Usage::
        # Admin login
        connection = syncano.connect(email='', password='')
        # OR
        connection = syncano.connect(api_key='')

        # User login
        connection = syncano.connect(username='', password='', api_key='', instance_name='')
        # OR
        connection = syncano.connect(user_key='', api_key='', instance_name='')
    """
    from syncano.connection import default_connection
    from syncano.models import registry

    default_connection.open(*args, **kwargs)
    instance = kwargs.get('instance_name', INSTANCE)

    if instance is not None:
        registry.set_default_instance(instance)
    return registry


def connect_instance(name=None, *args, **kwargs):
    """
    Connects with Syncano API and tries to load instance with provided name.

    :type name: string
    :param name: Chosen instance name

    :type email: string
    :param email: Your Syncano account email address

    :type password: string
    :param password: Your Syncano password

    :type api_key: string
    :param api_key: Your Syncano account key or instance api_key

    :type username: string
    :param username: Your Syncano username

    :type instance_name: string
    :param instance_name: Your Syncano instance_name

    :type verify_ssl: boolean
    :param verify_ssl: Verify SSL certificate

    :rtype: :class:`syncano.models.base.Instance`
    :return: Instance object

    Usage::

        # For Admin
        my_instance = syncano.connect_instance('my_instance_name', email='', password='')
        # OR
        my_instance = syncano.connect_instance('my_instance_name', api_key='')

        # For User
        my_instance = syncano.connect_instance(username='', password='', api_key='', instance_name='')
        # OR
        my_instance = syncano.connect_instance(user_key='', api_key='', instance_name='')
    """
    name = name or kwargs.get('instance_name', INSTANCE)
    kwargs['instance_name'] = name
    connection = connect(*args, **kwargs)
    return connection.Instance.please.get(name)


def social_connect():
    # curl -X POST \
    # -H "Authorization: token BACKEND_PROVIDER_TOKEN" \
    # -H "X-API-KEY: API_KEY" \
    # "https://api.syncano.io/v1/instances/instance/user/auth/backend_name/"
