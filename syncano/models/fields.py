import re
import six
from datetime import date, datetime

from syncano.exceptions import SyncanoFieldError


class Field(object):

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.model = None
        self.label = kwargs.pop('label', None)

        self.required = kwargs.pop('required', True)
        self.read_only = kwargs.pop('read_only', False)
        self.default = kwargs.pop('default', None)

        self.max_length = kwargs.pop('max_length', None)
        self.min_length = kwargs.pop('min_length', None)

        self.schema = kwargs

    def __get__(self, instance, owner):
        return instance._raw_data.get(self.name, self.default)

    def __set__(self, instance, value):
        self.validate(value, instance)
        instance._raw_data[self.name] = self.to_python(value)

    def __delete__(self, instance):
        if self.name in instance._raw_data:
            del instance._raw_data[self.name]

    def validate(self, value, model_instance):
        if self.required and not value:
            raise SyncanoFieldError(self.name, 'This field is required.')

        if self.read_only and getattr(model_instance, self.name):
            raise SyncanoFieldError(self.name, 'Field is read only.')

        if isinstance(value, six.string_types):
            if self.max_length and len(value) > self.max_length:
                raise SyncanoFieldError(self.name, 'Max length reached')

            if self.min_length and len(value) < self.min_length:
                raise SyncanoFieldError(self.name, 'Max length reached')

    def to_python(self, value):
        return value

    def to_native(self, value):
        return value

    def contribute_to_class(self, cls, name):
        self.model = cls
        cls._meta.add_field(self)

        if not self.name:
            self.name = name

        setattr(cls, name, self)


class StringField(Field):

    def to_python(self, value):
        if isinstance(value, six.string_types) or value is None:
            return value
        return six.u(value)


class IntegerField(Field):

    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise SyncanoFieldError(self.name, 'Invalid value.')


class FloatField(Field):

    def to_python(self, value):
        if value is None:
            return value
        try:
            return float(value)
        except (TypeError, ValueError):
            raise SyncanoFieldError(self.name, 'Invalid value.')


class BooleanField(Field):

    def to_python(self, value):
        if value in (True, False):
            return bool(value)

        if value in ('t', 'True', '1'):
            return True

        if value in ('f', 'False', '0'):
            return False

        raise SyncanoFieldError(self.name, 'Invalid value.')


class SlugField(StringField):
    regex = re.compile(r'^[-a-zA-Z0-9_]+$')

    def validate(self, value, model_instance):
        super(SlugField, self).validate(value, model_instance)
        if not bool(self.regex.search(value)):
            raise SyncanoFieldError(self.name, 'Invalid value.')
        return value


class EmailField(StringField):
    regex = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')

    def validate(self, value, model_instance):
        super(EmailField, self).validate(value, model_instance)

        if not value or '@' not in value:
            raise SyncanoFieldError(self.name, 'Enter a valid email address.')

        if not bool(self.regex.match(value)):
            raise SyncanoFieldError(self.name, 'Enter a valid email address.')


class ChoiceField(Field):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', [])
        self.allowed_values = [choice['value'] for choice in self.choices]
        super(ChoiceField, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super(ChoiceField, self).validate(value, model_instance)
        if self.choices and value not in self.allowed_values:
            raise SyncanoFieldError(self.name, 'Invalid choice.')


class DateField(Field):
    date_regex = re = re.compile(
        r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
    )

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        try:
            parsed = self.parse_date(value)
            if parsed is not None:
                return parsed
        except ValueError:
            pass

        raise SyncanoFieldError(self.name, 'Invalid date.')

    def parse_date(self, value):
        match = self.date_regex.match(value)
        if match:
            kw = {k: int(v) for k, v in six.iteritems(match.groupdict())}
            return date(**kw)

    def to_native(self, value):
        if isinstance(value, datetime.datetime):
            value = value.date()
        return value.isoformat()


class DateTimeField(DateField):
    FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, datetime):
            return value

        if isinstance(value, date):
            value = datetime(value.year, value.month, value.day)

        value = value.split('Z')[0]

        try:
            return datetime.strptime(value, self.FORMAT)
        except ValueError:
            pass

        try:
            parsed = self.parse_date(value)
            if parsed is not None:
                return datetime(parsed.year, parsed.month, parsed.day)
        except ValueError:
            pass

        raise SyncanoFieldError(self.name, 'Invalid value.')

    def to_native(self, value):
        if value is None:
            return value
        ret = value.isoformat()
        if ret.endswith('+00:00'):
            ret = ret[:-6] + 'Z'
        return ret


class ObjectField(Field):
    pass


class HyperlinkedField(ObjectField):
    METHOD_NAME = '_LINK'
    METHOD_PATTERN = 'get_{name}'
    IGNORED_LINKS = ('self', )

    def __init__(self, *args, **kwargs):
        self.links = kwargs.pop('links', [])
        super(HyperlinkedField, self).__init__(*args, **kwargs)


MAPPING = {
    'string': StringField,
    'integer': IntegerField,
    'float': FloatField,
    'boolean': BooleanField,
    'slug': SlugField,
    'email': EmailField,
    'choice': ChoiceField,
    'date': DateField,
    'datetime': DateTimeField,
    'field': Field,
    'links': HyperlinkedField,
}
