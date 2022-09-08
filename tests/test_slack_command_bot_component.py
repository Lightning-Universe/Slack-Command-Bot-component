r"""To test a lightning component:

1. Init the component.
2. call .run()
"""
import slack
from flask import request

from slack_command_bot import SlackCommandBot


class TestSlackCommandBot(SlackCommandBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_command(self):
        """Cutomize this method the way you want your bot to interact with the command."""

        data: dict = request.form
        channel_id = data["channel_id"]

        client = slack.WebClient(token=self.bot_token)
        client.chat_postMessage(channel=channel_id, text="Testing send msg")
        return "Hey there! command was received successfully", 200


def test_placeholder_component():
    messenger = TestSlackCommandBot()
    messenger.run()
    assert messenger.value == 1
