import hashlib
import os
import random
import re
import sys
import xml

import requests
import telepot
import telepot.helper

from datetime import datetime

from bs4 import BeautifulSoup

from peewee import (SqliteDatabase, Model, CharField, DateTimeField,
                    BooleanField, BigIntegerField, OperationalError)
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (per_chat_id, create_open, pave_event_space,
                              include_callback_query_chat_id)
from uritools import urisplit

"""
A minimal bot that just ask a question and answer accordingly you asked yes/no.

You must register this bot with BotFather. 

Then, create a token for it and set as an environment variable: 

    $ export PYLE_BOT_TOKEN=your-bot-token-here
"""

BOT_TOKEN = os.environ.get('PYLE_BOT_TOKEN', '')
BOT_TOKEN_NOT_FOUND_MESSAGE = '''
    Environment variable BOT_TOKEN not set. You must e.g..:
        $ export PYLE_BOT_TOKEN=your-bot-token-here
'''
URL_REGEX = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
PYLE_RESPONSES = ['saved', 'duplicated', 'error']


def bootstrap_database():
    db = SqliteDatabase('pylebot.db')
    try:
        db.create_tables([UrlsHistory])
    except OperationalError as ex:
        print('Ignorirg exception: {}'.format(ex))


class UrlsHistory(Model):
    id = BigIntegerField(primary_key=True)
    url = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.now())
    saved_to_pyle = BooleanField(default=False)

    class Meta:
        database = SqliteDatabase('pylebot.db')


class MessageHandler(telepot.helper.ChatHandler):

    def on_chat_message(self, msg):
        input = msg['text']
        url = self._is_url(input)
        if url:
            stripped_url = self._strip_unnecessary_url_parameters(url)
            sqlite_id = msg['date']

            # passing sqlite_id here is a trick so I can recover info from the database on handling the callback.
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='Yes', callback_data='yes.{}'.format(sqlite_id)),
                InlineKeyboardButton(text='No', callback_data='no.no'),
            ]])
            self.sender.sendMessage('Do you want me to send "{}" to pyle?'.format(stripped_url),
                                    reply_markup=keyboard)
        else:
            message = ('Sorry, not a URL. I just accept URLs '
                       '(those that start with http[s]), so I cannot do '
                       'anything with that.')
            self.sender.sendMessage(message)

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg,
                                                       flavor='callback_query')

        confirmation, sqlite_id = query_data.split('.')

        if confirmation == 'yes':
            url = 'blablabla'  # # TODO: get the url here from sqlite
            self.bot.answerCallbackQuery(query_id, text='Sending {} to pyle...'.format(url))
            response = self.send_to_pyle('the-url-here')
            if response == 'error':
                self.sender.sendMessage('TOO BAD :( I could not send {} to pyle. '
                                        'You could retry manually later.'.format(url))
            elif response == 'saved':
                self.sender.sendMessage('DONE :) {} is now on pyle.'.format(url))
            elif response == 'duplicated':
                self.sender.sendMessage('Nothing to do, {} is already on pyle.'.format(url))

        else:
            self.bot.answerCallbackQuery(query_id, text='So I will do nothing :(')
            self.close()

    def send_to_pyle(self, url):
        # TODO: Must be properly implemented, this is just a mock.
        response = random.choice(PYLE_RESPONSES)
        return response

    def _is_url(self, input):
        url = None
        for text in input.split('\n'):
            if text.startswith('http'):
                url = text
                break
        if not url:
            try:
                url = re.findall(URL_REGEX, input)[0]
            except IndexError:
                pass

        return url

    def _get_text_from_html(self, html):
        soup = BeautifulSoup(html)

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text.encode('utf-8')

    def _strip_unnecessary_url_parameters(self, url):
        parsed = urisplit(url)

        if parsed.query:
            original_response = requests.get(url)

            original_content = self._get_text_from_html(original_response.content)

            original_md5 = hashlib.md5(original_content).hexdigest()

            url_without_query = '{}://{}{}'.format(parsed.scheme, parsed.authority, parsed.path)
            no_query_response = requests.get(url_without_query)

            no_query_content = self._get_text_from_html(no_query_response.content)

            no_query_md5 = hashlib.md5(no_query_content).hexdigest()

            if original_md5 == no_query_md5:
                return url_without_query

        return url

def main():
    if not BOT_TOKEN:
        print(BOT_TOKEN_NOT_FOUND_MESSAGE)
        sys.exit(1)

    try:
        bootstrap_database()

        bot = telepot.DelegatorBot(BOT_TOKEN, [
            include_callback_query_chat_id(
                pave_event_space())(
                    per_chat_id(types=['private']), create_open,
                MessageHandler, timeout=10),
        ])

        urls = UrlsHistory.select().order_by('-created_at')

        bot.message_loop(
            run_forever='At your service. '
                        'There are {} urls '
                        'on the history.'.format(urls.count())
        )
    except KeyboardInterrupt:
        print('Finishing by your request. Bye!\n')
        sys.exit(0)

if __name__ == '__main__':
    main()
