from django.apps import apps
from django.test import SimpleTestCase
from apps.users.apps import UsersConfig

class UsersConfigTest(SimpleTestCase):
    def test_apps_config(self):
        self.assertEqual(UsersConfig.name, 'apps.users')
        self.assertEqual(apps.get_app_config('users').name, 'apps.users')