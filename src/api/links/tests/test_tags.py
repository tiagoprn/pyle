from datetime import datetime, timedelta
from time import sleep

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from links.models import Tag, Link


class TagTests(APITestCase):
    users = {
        '1': {'username': 'first',
              'email': 'first@first.com',
              'password': 'aBc12345',
              'is_staff': True},
        '2': {'username': 'second',
              'email': 'second@second.com',
              'password': 'BcD23456',
              'is_staff': True},
        '3': {'username': 'no-admin',
              'email': 'no@admin.com',
              'password': 'cDe34567',
              'is_staff': False}
    }


    def create_user(self, user_number):
        user = User(username=self.users[user_number]['username'],
                    email=self.users[user_number]['email'],
                    is_staff=self.users[user_number]['is_staff'])
        user.set_password(self.users[user_number]['password'])
        user.save()
        return user

    def create_token_for_user(self, user_number):
        user = User.objects.filter(username=self.users[user_number][
            'username']).first() or self.create_user(user_number)

        url = reverse('api-token-auth')
        data = {'username': self.users[user_number]['username'],
                'password': self.users[user_number]['password']}
        response = self.client.post(url, data, format='json')
        return response.data.get('token', ''), user

    def get_authorization_header_with_token_and_user_instance(self, user_number):
        # The header name must be "HTTP_AUTHORIZATION" for the django test client,
        # simply "Authorization" like with curl won't work.
        token, user = self.create_token_for_user(user_number)
        return {'HTTP_AUTHORIZATION': 'JWT {}'.format(token)}, user

    def create_tag(self, name, user_number):
        auth_header, user = self.get_authorization_header_with_token_and_user_instance(user_number)
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        url = reverse('tag-list')
        data = {'name': name}
        response = self.client.post(url, data, format='json', **auth_header)
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
        self.create_tag(second_tag_name, '1')
        url = reverse('tag-list')
        auth_header, _ = self.get_authorization_header_with_token_and_user_instance('1')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        response = self.client.get(url, format='json', **auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        # Remember: tags are brought on alphabetical order
        self.assertEqual(response.data['results'][0]['name'], second_tag_name)
        self.assertEqual(response.data['results'][0]['owner'], self.users['1']['username'])
        self.assertEqual(response.data['results'][1]['name'], first_tag_name)
        self.assertEqual(response.data['results'][1]['owner'], self.users['1']['username'])

    def test_update_tag(self):
        new_tag_name = 'Initial'
        response, user = self.create_tag(new_tag_name, '1')
        url = response.data['url']
        updated_tag_name = 'InitialUPDATED'
        data = {'name': updated_tag_name}
        auth_header, _ = self.get_authorization_header_with_token_and_user_instance('1')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        patch_response = self.client.patch(url, data, format='json', **auth_header)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['name'], updated_tag_name)

    def test_delete_tag(self):
        new_tag_name = 'Initial'
        response, user = self.create_tag(new_tag_name, '1')
        self.assertEqual(Tag.objects.count(), 1)
        url = response.data['url']
        auth_header, _ = self.get_authorization_header_with_token_and_user_instance('1')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        delete_response = self.client.delete(url, format='json', **auth_header)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.count(), 0)

    def test_filter_tag_by_name(self):
        tag_name1 = 'First'
        self.create_tag(tag_name1, '1')
        tag_name2 = 'Second'
        self.create_tag(tag_name2, '1')
        filter_by_name = {'name': tag_name1}
        url = '{}?{}'.format(reverse('tag-list'), urlencode(filter_by_name))
        auth_header, _ = self.get_authorization_header_with_token_and_user_instance('1')
        response = self.client.get(url, format='json', **auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], tag_name1)


    def test_should_not_list_other_users_tags(self):
        self.create_tag('First', '1')
        self.create_tag('Second', '2')
        self.create_tag('Third', '3')

        url = reverse('tag-list')
        self.assertEqual(Tag.objects.count(), 3)

        auth_header, _ = self.get_authorization_header_with_token_and_user_instance('3')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        response = self.client.get(url, format='json', **auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        # Remember: tags are brought on alphabetical order
        self.assertEqual(response.data['results'][0]['name'], 'Third')
        self.assertEqual(response.data['results'][0]['owner'], self.users['3']['username'])

    def test_should_not_update_other_users_tags(self):
        new_tag_name = 'Initial'
        response, user = self.create_tag(new_tag_name, '1')
        url = response.data['url']
        updated_tag_name = 'InitialUPDATED'
        data = {'name': updated_tag_name}
        # since I don't know if below really works, this approach seems better: https://djangosnippets.org/snippets/850/

        auth_header, _ = self.get_authorization_header_with_token_and_user_instance('3')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        patch_response = self.client.patch(url, data, format='json', **auth_header)  # TODO: pass the token here

        self.assertEqual(patch_response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_should_not_delete_other_users_tags(self):
        new_tag_name = 'Initial'
        response, user = self.create_tag(new_tag_name, '1')
        url = response.data['url']

        auth_header, _ = self.get_authorization_header_with_token_and_user_instance('3')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        patch_response = self.client.delete(url, format='json', **auth_header)
        self.assertEqual(patch_response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
