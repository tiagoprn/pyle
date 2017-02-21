from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APITestCase

# from ..models import Tag, Link

# TODO: Include tests for the token generation also. Check if on creation of a new token before the previous one expiration, the older one gets invalid.
# TODO: If not, search on djangorestframework-jwt documentation if there is a way to revoke a token.
# TODO: Test with 2 users, one that owns and other not the specific resources.


class AuthTests(APITestCase):
    # urls = 'api.urls'
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

        # create the first token for the user
        url = reverse('api-token-auth')
        data = {'username': self.users['1']['username'],
                'password': self.users['1']['password']}
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        token1 = response1.data['token']
        print('\nTOKEN 1: {}'.format(token1))

        # check the first token is valid
        url = reverse('api-token-verify')
        data = {'token': token1}
        verified1 = self.client.post(url, data, format='json')
        self.assertEqual(verified1.status_code, status.HTTP_200_OK)

        # TODO: Generate a new test from this one, setting the time to higher than settings.JWT_AUTH.JWT_EXPIRATION_DELTA.
        #       On this new test, token1 and token2 must be DIFFERENT.

        # import time
        # time.sleep(35)  # forcing the token expiration

        # try to create a second token for the user
        url = reverse('api-token-auth')
        data = {'username': self.users['1']['username'],
                'password': self.users['1']['password']}
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        token2 = response2.data['token']
        print('\nTOKEN 2: {}'.format(token2))

        # both tokens must be equal (because of the first hasn't expired yet)
        self.assertEqual(token1, token2)

