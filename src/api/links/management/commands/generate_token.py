from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from rest_framework_jwt.settings import api_settings


class Command(BaseCommand):
    help = 'Generate token for a specific user.'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **options):
        username = options['username'][0]
        user = User.objects.filter(username=username).first()
        if not user:
            raise CommandError('User "{}" does not exist'.format(options['username']))

        # http://getblimp.github.io/django-rest-framework-jwt/#creating-a-new-token-manually

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        self.stdout.write(
            self.style.SUCCESS(
                'Use the following token for the user "{}": \n{}'.format(
                    username, token)))
