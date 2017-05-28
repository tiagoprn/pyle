import os
import sys
import time
import telepot
import telepot.helper

from datetime import datetime

from peewee import SqliteDatabase, Model, CharField, DateTimeField, BooleanField, OperationalError
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)

"""
A minimal bot that just ask a question and answer accordingly you asked yes/no.

You must register this bot with BotFather. 

Then, create a token for it and set as an environment variable: 

    $ export PYLE_BOT_TOKEN=your-bot-token-here
"""

def bootstrap_database():
    db = SqliteDatabase('pylebot.db')
    try:
        db.create_tables([UrlsHistory])
    except OperationalError as ex:
        print('Ignorirg exception: {}'.format(ex))


class UrlsHistory(Model):
    url = CharField(primary_key=True)
    created_at = DateTimeField(default=datetime.now())
    saved_to_pyle = BooleanField(default=False)

    class Meta:
        database = SqliteDatabase('pylebot.db')


class MessageHandler(telepot.helper.ChatHandler):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Yes', callback_data='yes'),
                   InlineKeyboardButton(text='No.', callback_data='no'),
               ]])

    def _ask(self):
         self.sender.sendMessage('Do you want something?', reply_markup=self.keyboard)

    def on_chat_message(self, msg):
        self._ask()

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if query_data == 'yes':
            self.sender.sendMessage('I can do it!!')
            self.close()
        else:
            self.bot.answerCallbackQuery(query_id, text='Ok. But I am going to keep asking.')
            self._ask()

    def on_close(self, ex):
        print("Closing now... ")


def main():
    BOT_TOKEN = os.environ.get('PYLE_BOT_TOKEN', '')
    BOT_TOKEN_NOT_FOUND_MESSAGE = '''
        Environment variable BOT_TOKEN not set. You must e.g..:
            $ export PYLE_BOT_TOKEN=your-bot-token-here
    '''
    if not BOT_TOKEN:
        print(BOT_TOKEN_NOT_FOUND_MESSAGE)
        sys.exit(1)

    try:
        bootstrap_database()

        bot = telepot.DelegatorBot(BOT_TOKEN, [
            include_callback_query_chat_id(
                pave_event_space())(
                    per_chat_id(types=['private']), create_open, MessageHandler, timeout=10),
        ])

        urls = UrlsHistory.select().order_by('-created_at')

        bot.message_loop(run_forever='At your service. There are {} urls on the history.'.format(urls.count()))
    except KeyboardInterrupt:
        print('Finishing by your request. Bye!\n')
        sys.exit(0)

if __name__ == '__main__':
    main()
