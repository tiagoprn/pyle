from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

# from ..models import Tag, Link

# TODO: Test with 2 users, one that owns and other not the specific resources.
# TODO: Make sure to login with self.client.login() for the permissions to be verified.


class TagTests(APITestCase):
    users = {
        '1': {'username': 'first',
              'email': 'first@first.com',
              'password': 'aBc12345',
              'is_staff': True},
        '2': {'username': 'second',
              'email': 'second@second.com',
              'password': 'BcD23456',
              'is_staff': True}
    }

    def create_admin_user(self, user_number):
        user = User(username=self.users[user_number]['username'],
                    email=self.users[user_number]['email'],
                    is_staff=self.users[user_number]['is_staff'])
        user.set_password(self.users[user_number]['password'])
        user.save()
        return user

    def test_create_user_and_its_token(self):
        user = self.create_admin_user('1')
        users = User.objects.filter(username=self.users['1']['username'])
        self.assertEqual(users.count(), 1)
        user_created = users.first()
        self.assertEqual(user_created.username, self.users['1']['username'])

        # create the first token for the user
        url = reverse('api-token-auth')
        data = {'username': self.users['1']['username'],
                'password': self.users['1']['password']}
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        token1 = response1.data['token']
        self.assertIsNotNone(token1)
        return token1

    def test_create_tag(self):
        pass



class LinkTests(APITestCase):
    pass

