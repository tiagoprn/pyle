from telepot.delegate import pave_event_space, per_chat_id, create_open

import os
import datetime

import telepot

"""
You must register this bot with BotFather. 

Then, create a token for it and set as an environment variable: 

    $ export PYLE_BOT_TOKEN=your-bot-token-here

Available commands:
    - `/hi` - reply with the current time.
    
Reference: http://telepot.readthedocs.io/en/latest/    
"""

BOT_TOKEN = os.environ.get('PYLE_BOT_TOKEN', '')
BOT_TOKEN_NOT_FOUND_MESSAGE = '''
    Environment variable BOT_TOKEN not set. You must e.g..:
        $ export PYLE_BOT_TOKEN=your-bot-token-here
'''
AVAILABLE_COMMANDS = [
    '/hi'
]


class MessageHandler(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        # chat_id = msg['chat']['id']
        chat_user = msg['chat']['first_name']
        command = msg['text']

        print('msg: {}'.format(repr(msg)))

        if command == '/hi':
            self.sender.sendMessage('Hi {}, welcome! Now is {}.'.format(chat_user,
                                    str(datetime.datetime.now())))
        else:
            self.sender.sendMessage(
                'Sorry {}, I do not recognize this command. '
                'Available commands: {}'.format(chat_user, ', '.join(AVAILABLE_COMMANDS)))


def main():
    bot = telepot.DelegatorBot(BOT_TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, MessageHandler, timeout=10),
    ])
    bot.message_loop(run_forever='At your service ...')

main()
