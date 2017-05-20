import os
import sys

import telepot

from datetime import datetime
from urllib.parse import urlparse

from telepot.delegate import pave_event_space, per_chat_id, create_open

"""
You must register this bot with BotFather. 

Then, create a token for it and set as an environment variable: 

    $ export PYLE_BOT_TOKEN=your-bot-token-here
    
References: 
http://telepot.readthedocs.io/en/latest/
https://github.com/nickoala/telepot/blob/master/test/test3_send.py
https://core.telegram.org/bots/api#sendmessage
https://core.telegram.org/bots/api/#keyboardbutton    
"""
AVAILABLE_COMMANDS = [
    '/hi'  # Greets the user with the current time
]
BOT_TOKEN = os.environ.get('PYLE_BOT_TOKEN', '')
BOT_TOKEN_NOT_FOUND_MESSAGE = '''
    Environment variable BOT_TOKEN not set. You must e.g..:
        $ export PYLE_BOT_TOKEN=your-bot-token-here
'''


class MessageHandler(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        # chat_id = msg['chat']['id']
        chat_user = msg['chat']['first_name']
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
                'Available commands: {}'.format(chat_user, ', '.join(AVAILABLE_COMMANDS)))



def main():
    if not BOT_TOKEN:
        print(BOT_TOKEN_NOT_FOUND_MESSAGE)
        sys.exit(1)

    try:
        bot = telepot.DelegatorBot(BOT_TOKEN, [
            pave_event_space()(
                per_chat_id(), create_open, MessageHandler, timeout=10),
        ])
        bot.message_loop(run_forever='At your service ...')
    except KeyboardInterrupt:
        print('Finishing by your request. Bye!\n')
        sys.exit(0)

if __name__ == '__main__':
    main()
