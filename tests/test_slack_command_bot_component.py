r"""To test a lightning component:

1. Init the component.
2. call .run()
"""
import threading
import time

import requests

from slack_command_bot import SlackCommandBot


class TestSlackCommandBot(SlackCommandBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_command(self):
        return "Hey there! command was received successfully", 200


def test_placeholder_component():
    slack_bot = TestSlackCommandBot(command="/test")
    th = threading.Thread(target=slack_bot.run, daemon=True)
    th.start()
    time.sleep(10)
    requests.get(f"http://localhost:{slack_bot.port}/test").raise_for_status()
