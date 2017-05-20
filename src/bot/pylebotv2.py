import os
import sys
import time

import telepot

from urllib.parse import urlparse

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

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

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    received_text = msg['text']

    # TODO: If I have sent a url, e.g. sharing from Firefox to Telegram, this will break.
    # So, I will treat it differently here. Maybe put the url on an sqlite database to
    # retrieve always the late one entered?

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Press me', callback_data=received_text)],
               ])

    bot.sendMessage(chat_id, 'Use inline keyboard', reply_markup=keyboard)

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    bot.answerCallbackQuery(query_id, text='ROGER ROGER!')

if not BOT_TOKEN:
    print(BOT_TOKEN_NOT_FOUND_MESSAGE)
    sys.exit(1)

try:
    bot = telepot.Bot(BOT_TOKEN)
    print('At your service...')
    MessageLoop(bot, {'chat': on_chat_message,
                      'callback_query': on_callback_query},

                ).run_forever(timeout=10)
except KeyboardInterrupt:
    print('Finishing by your request. Bye!\n')
    sys.exit(0)

