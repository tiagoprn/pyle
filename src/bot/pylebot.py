import os
import sys

import telepot

from telepot.delegate import pave_event_space, per_chat_id, create_open

if __name__ == '__main__':
    from commands import Command
else:
    from .commands import Command


"""
You must register this bot with BotFather. 

Then, create a token for it and set as an environment variable: 

    $ export PYLE_BOT_TOKEN=your-bot-token-here
    
Reference: http://telepot.readthedocs.io/en/latest/    
"""

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
        command = Command(sender=self.sender, chat_user=chat_user)
        command.do(msg['text'])


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
