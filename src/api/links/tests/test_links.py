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

# TODO: Test with 2 users, one that owns and other not the specific resources.
# TODO: Make sure to login with self.client.login() for the permissions to be verified.


class LinkTests(APITestCase):
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

    links = {
        '1': {
            "uri": "http://link1.com",
            "name": "link1",
            "notes": None,
            "content": None,
            "content_last_updated_at": None,
            "tags": [{"name": "first"}, {"name": "general"}]
        },
        '2': {
            "uri": "http://link2.com",
            "name": "link2",
            "notes": None,
            "content": None,
            "content_last_updated_at": None,
            "tags": [{"name": "second"}, {"name": "general"}]
        }
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

    def create_link(self, user_number, link_number):
        auth_header, user = self.get_authorization_header_with_token_and_user_instance(user_number)
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        url = reverse('link-list')
        data = self.links[link_number]
        response = self.client.post(url, data, format='json', **auth_header)
        return response, user

    def test_create_and_retrieve_links(self):
        response, user = self.create_link('1', '1')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check the link created
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(Link.objects.get().name, self.links['1']['name'])
        self.assertEqual(Link.objects.get().uri, self.links['1']['uri'])
        self.assertEqual(Link.objects.get().owner, user)
        # check the tags created for the link
        self.assertEqual(Tag.objects.count(), 2)
        tags = Tag.objects.all()
        for index, tag in enumerate(tags):
            self.assertEqual(tag.name, self.links['1']['tags'][index]['name'])

    def test_create_duplicated_link(self):
        response1, user1 = self.create_link('1', '1')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2, user2 = self.create_link('1', '1')
        self.assertEqual(response2.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_retrieve_link_list(self):
        self.create_link('1', '1')
        self.create_link('1', '2')
        url = reverse('link-list')
        auth_header, user = self.get_authorization_header_with_token_and_user_instance('1')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        response = self.client.get(url, format='json', **auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        # Remember: tags are brought most-recent-first
        self.assertEqual(response.data['results'][0]['name'], 'link2')
        self.assertEqual(response.data['results'][0]['owner'], self.users['1']['username'])
        self.assertEqual(response.data['results'][1]['name'], 'link1')
        self.assertEqual(response.data['results'][1]['owner'], self.users['1']['username'])

    def test_update_link(self):
        response1, user1 = self.create_link('1', '1')
        self.create_link('2', '2')

        url = response1.data['url']
        new_link_name = 'link1 UPDATED'

        data = {'name': new_link_name}
        auth_header, user = self.get_authorization_header_with_token_and_user_instance('1')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        patch_response = self.client.patch(url, data, format='json', **auth_header)

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['name'], new_link_name)

    def test_delete_link(self):
        response, user = self.create_link('2', '2')
        self.assertEqual(Link.objects.count(), 1)
        url = response.data['url']
        auth_header, user = self.get_authorization_header_with_token_and_user_instance('2')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        delete_response = self.client.delete(url, format='json', **auth_header)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Link.objects.count(), 0)

    def test_filter_link_by_name(self):
        self.create_link('1', '1')
        self.create_link('1', '2')
        filter_by_name = {'name': self.links['1']['name']}
        url = '{}?{}'.format(reverse('link-list'), urlencode(filter_by_name))
        auth_header, user = self.get_authorization_header_with_token_and_user_instance('1')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        response = self.client.get(url, format='json', **auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], self.links['1']['name'])

    def test_should_not_retrieve_other_user_links(self):
        self.create_link('1', '1')
        self.create_link('1', '2')
        self.assertEqual(Link.objects.count(), 2)
        url = reverse('link-list')
        auth_header, user = self.get_authorization_header_with_token_and_user_instance('2')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        response = self.client.get(url, format='json', **auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_should_not_update_other_user_link(self):
        response, user = self.create_link('1', '1')
        self.assertEqual(Link.objects.count(), 1)

        url = response.data['url']
        new_link_name = 'link1 UPDATED'
        data = {'name': new_link_name}

        auth_header, user = self.get_authorization_header_with_token_and_user_instance('2')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        patch_response = self.client.patch(url, data, format='json', **auth_header)

        self.assertEqual(patch_response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_should_not_delete_other_user_link(self):
        response, user = self.create_link('2', '2')
        self.assertEqual(Link.objects.count(), 1)
        url = response.data['url']
        auth_header, user = self.get_authorization_header_with_token_and_user_instance('1')
        sleep(0.1)  # FIXME: This looks like cheating, check why it is necessary
        delete_response = self.client.delete(url, format='json', **auth_header)
        self.assertEqual(delete_response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(Link.objects.count(), 1)
