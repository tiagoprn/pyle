from datetime import datetime

AVAILABLE_COMMANDS = [
    '/hi'  # Greets the user with the current time
]


class Command(object):
    def __init__(self, sender, **kwargs):
        self.sender = sender
        self.chat_user = kwargs.get('chat_user', 'SOMEONE')

    def do(self, command):
        # TODO: refactor this if to the dict+function_name design pattern
        if command == '/hi':
            self.sender.sendMessage('Hi {}, welcome! Now is {}.'.format(self.chat_user,
                                    str(datetime.now())))
        else:
            self.sender.sendMessage(
                'Sorry {}, I do not recognize this command. '
                'Available commands: {}'.format(self.chat_user, ', '.join(AVAILABLE_COMMANDS)))
