from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from links.models import Tag, Link

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

    def create_user(self, user_number):
        user = User(username=self.users[user_number]['username'],
                    email=self.users[user_number]['email'],
                    is_staff=self.users[user_number]['is_staff'])
        user.set_password(self.users[user_number]['password'])
        user.save()
        return user

    def create_token_for_user(self, user_number):
        url = reverse('api-token-auth')
        data = {'username': self.users[user_number]['username'],
                'password': self.users[user_number]['password']}
        response = self.client.post(url, data, format='json')
        return response.data['token']

    def create_tag(self, name, user_number):
        user = User.objects.filter(username=self.users[user_number][
            'username']).first() or self.create_user(user_number)

        token = self.create_token_for_user(user_number)
        self.client.login(username=self.users[user_number]['username'],
                          password=self.users[user_number]['password'])
        url = reverse('tag-list')
        data = {'name': name}
        response = self.client.post(url, data, format='json')
        return response, user

    def test_create_and_retrieve_tag(self):
        new_tag_name = 'BeatIt'
        response, user = self.create_tag(new_tag_name, '1')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.get().name, new_tag_name)
        self.assertEqual(Tag.objects.get().owner, user)

    def test_create_duplicated_tag(self):
        new_tag_name = 'BeatIt'
        response1, user1 = self.create_tag(new_tag_name, '1')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2, user2 = self.create_tag(new_tag_name, '1')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)

    def test_retrieve_tag_list(self):
        first_tag_name = 'Some'
        self.create_tag(first_tag_name, '1')
        second_tag_name = 'Any'
        self.create_tag(second_tag_name, '2')
        url = reverse('tag-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        # Remember: tags are brought on alphabetical order
        self.assertEqual(response.data['results'][0]['name'], second_tag_name)
        self.assertEqual(response.data['results'][0]['owner'], self.users['2']['username'])
        self.assertEqual(response.data['results'][1]['name'], first_tag_name)
        self.assertEqual(response.data['results'][1]['owner'], self.users['1']['username'])

    def test_update_tag(self):
        new_tag_name = 'Initial'
        response, user = self.create_tag(new_tag_name, '1')
        url = response.data['url']
        updated_tag_name = 'InitialUPDATED'
        data = {'name': updated_tag_name}
        patch_response = self.client.patch(url, data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['name'], updated_tag_name)

    def test_delete_tag(self):
        new_tag_name = 'Initial'
        response, user = self.create_tag(new_tag_name, '1')
        self.assertEqual(Tag.objects.count(), 1)
        url = response.data['url']
        delete_response = self.client.delete(url, format='json')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.count(), 0)

    def test_filter_tag_by_name(self):
        tag_name1 = 'First'
        self.create_tag(tag_name1, '1')
        tag_name2 = 'Second'
        self.create_tag(tag_name2, '1')
        filter_by_name = {'name': tag_name1}
        url = '{}?{}'.format(reverse('tag-list'), urlencode(filter_by_name))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], tag_name1)
