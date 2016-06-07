# -*- coding: utf-8 -*-
from syncano.models import User
from tests.integration_test import InstanceMixin, IntegrationTest


class UserProfileTest(InstanceMixin, IntegrationTest):

    @classmethod
    def setUpClass(cls):
        super(UserProfileTest, cls).setUpClass()
        cls.user = cls.instance.users.create(
            username='JozinZBazin',
            password='jezioro',
        )
        cls.SAMPLE_PROFILE_PIC = 'some_url_here'

    def test_profile(self):
        self.assertTrue(self.user.profile)
        self.assertEqual(
            self.user.profile.__class__.__name__,
            '{}UserProfileObject'.format(self.instance.name.title())
        )

    def test_profile_klass(self):
        klass = self.user.profile.get_class_object()
        self.assertTrue(klass)
        self.assertEqual(klass.instance_name, self.instance.name)

    def test_profile_change_schema(self):
        klass = self.user.profile.get_class_object()
        klass.schema = [
            {'name': 'profile_pic', 'type': 'string'}
        ]

        klass.save()
        self.user.reload()  # force to refresh profile model;

        self.user.profile.profile_pic = self.SAMPLE_PROFILE_PIC
        self.user.save()
        user = User.please.get(id=self.user.id)
        self.assertEqual(user.profile.profile_pic, self.SAMPLE_PROFILE_PIC)
