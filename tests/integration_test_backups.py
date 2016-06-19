# -*- coding: utf-8 -*-
from syncano.models import Backup
from tests.integration_test import InstanceMixin, IntegrationTest


class FullBackupTestCase(InstanceMixin, IntegrationTest):

    def _test_backup_create(self):
        new_backup = Backup()
        backup_test = new_backup.save()

        backup = Backup.please.get(id=backup_test.id)
        self.assertTrue(backup)
        self.assertEqual(backup.id, backup_test.id)
        self.assertEqual(backup.author.email, self.API_EMAIL)

        return backup.id

    def _test_backup_detail(self, backup_id):
        backup = Backup.please.get(id=backup_id)

        self.assertEqual(backup.id, backup_id)
        self.assertEqual(backup.author.email, self.API_EMAIL)

    def _test_backup_list(self):

        backups = [backup for backup in Backup.please.list()]
        self.assertTrue(len(backups))  # at least one backup here;

    def _test_backup_delete(self, backup_id):
        backup = Backup.please.get(id=backup_id)
        backup.delete()
        backups = [backup_object for backup_object in Backup.please.list()]
        self.assertEqual(len(backups), 0)

    def test_backup(self):
        # we provide one test for all functionality to avoid creating too many backups;
        backup_id = self._test_backup_create()
        self._test_backup_list()
        self._test_backup_detail(backup_id=backup_id)
        self._test_backup_delete(backup_id=backup_id)
