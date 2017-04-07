import os
import time
import random
import datetime
import telepot

"""
You must register this bot with BotFather. 

Then, create a token for it and set as an environment variable: 

    $ export PYLE_BOT_TOKEN=your-bot-token-here

Available commands:
- `/roll` - reply with a random integer between 1 and 6, like rolling a dice.
- `/time` - reply with the current time, like a clock.
"""

BOT_TOKEN = os.environ.get('PYLE_BOT_TOKEN', '')


def handle(msg):
    chat_id = msg['chat']['id']
    chat_user = msg['chat']['first_name']
    command = msg['text']

    print('msg: {}'.format(repr(msg)))

    if command == '/hi':
        bot.sendMessage(chat_id,
                        'Hi {}, welcome! Now is {}.'.format(chat_user,
                                                            str(datetime.datetime.now())))
    

bot = telepot.Bot(BOT_TOKEN)
bot.message_loop(handle)
print('I am listening ...')

while 1:
    time.sleep(10)