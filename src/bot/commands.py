import telepot

from datetime import datetime
from urllib.parse import urlparse

AVAILABLE_COMMANDS = [
    '/hi'  # Greets the user with the current time
]


'''
https://github.com/nickoala/telepot/blob/master/test/test3_send.py
https://core.telegram.org/bots/api#sendmessage
https://core.telegram.org/bots/api/#keyboardbutton
'''

class Command(object):
    def __init__(self, sender, **kwargs):
        self.sender = sender
        self.chat_user = kwargs.get('chat_user', 'SOMEONE')

    def do(self, msg):
        command = msg['text']

        print('MESSAGE ID: {}'.format(msg['message_id']))

        # TODO: Fix this bug, it is not correctly detecting the URLs
        url = urlparse(command).geturl()
        is_url = True if url else False
        import ipdb; ipdb.set_trace()

        # TODO: refactor this if to the dict+function_name design pattern
        if command == '/hi':
            self.sender.sendMessage('Hi {}, welcome! Now is {}.'.format(self.chat_user,
                                    str(datetime.now())))
        elif is_url:
            show_keyboard = {'keyboard': [['Yes', 'No']], 'resize_keyboard': True}
            self.sender.sendMessage(
                'I have detected you entered this URL: \n {}. Do you confirm?'.format(command),
                reply_markup=show_keyboard,
                reply_to_message_id=msg['message_id']
            )
        else:
            self.sender.sendMessage(
                'Sorry {}, I do not recognize this command. '
                'Available commands: {}'.format(self.chat_user, ', '.join(AVAILABLE_COMMANDS)))
