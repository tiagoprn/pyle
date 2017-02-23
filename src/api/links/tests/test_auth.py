from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
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

    def test_create_user_and_its_token_with_first_token_not_expired_yet(self):
        user = self.create_admin_user('1')
        users = User.objects.filter(username=self.users['1']['username'])
        self.assertEqual(users.count(), 1)
        user_created = users.first()
        self.assertEqual(user_created.username, self.users['1']['username'])

        now = datetime.strptime('2016-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        token1_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        with freeze_time(token1_timestamp):
            # create the first token for the user
            url = reverse('api-token-auth')
            data = {'username': self.users['1']['username'],
                    'password': self.users['1']['password']}
            response1 = self.client.post(url, data, format='json')
            self.assertEqual(response1.status_code, status.HTTP_200_OK)

            token1 = response1.data['token']

        now = now + timedelta(seconds=10)
        token2_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        with freeze_time(token2_timestamp):
            # try to create a second token for the user
            url = reverse('api-token-auth')
            data = {'username': self.users['1']['username'],
                    'password': self.users['1']['password']}
            response2 = self.client.post(url, data, format='json')
            self.assertEqual(response2.status_code, status.HTTP_200_OK)

            token2 = response2.data['token']

            # check the first token is still valid
            url = reverse('api-token-verify')
            data = {'token': token1}
            verified1 = self.client.post(url, data, format='json')
            self.assertEqual(verified1.status_code, status.HTTP_200_OK)

            # tokens must be different
            self.assertNotEqual(token1, token2)

    def test_create_user_and_its_token_with_first_token_expired(self):
        user = self.create_admin_user('1')
        users = User.objects.filter(username=self.users['1']['username'])
        self.assertEqual(users.count(), 1)
        user_created = users.first()
        self.assertEqual(user_created.username, self.users['1']['username'])

        now = datetime.strptime('2016-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        token1_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        with freeze_time(token1_timestamp):
            # create the first token for the user
            url = reverse('api-token-auth')
            data = {'username': self.users['1']['username'],
                    'password': self.users['1']['password']}
            response1 = self.client.post(url, data, format='json')
            self.assertEqual(response1.status_code, status.HTTP_200_OK)

            token1 = response1.data['token']

        now = now + settings.JWT_AUTH['JWT_EXPIRATION_DELTA'] + timedelta(seconds=1)
        token2_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        with freeze_time(token2_timestamp):
            # try to create a second token for the user
            url = reverse('api-token-auth')
            data = {'username': self.users['1']['username'],
                    'password': self.users['1']['password']}
            response2 = self.client.post(url, data, format='json')
            self.assertEqual(response2.status_code, status.HTTP_200_OK)

            token2 = response2.data['token']

            # check the first token is not valid anymore
            url = reverse('api-token-verify')
            data = {'token': token1}
            verified1 = self.client.post(url, data, format='json')
            self.assertEqual(verified1.status_code, status.HTTP_400_BAD_REQUEST)

            # tokens must be different
            self.assertNotEqual(token1, token2)
