import os

import lightning as L
import slack
from flask import request

from slack_command_bot import SlackCommandBot


class DemoSlackCommandBot(SlackCommandBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_command(self):
        """Customize this method the way you want your bot to interact with the command."""

        data: dict = request.form
        client = slack.WebClient(token=self._bot_token)
        client.chat_postMessage(channel=data.get("channel_id"), text="Testing send msg")
        return "Hey there! command was received successfully", 200


class LitApp(L.LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.slack_command_bot = DemoSlackCommandBot()

    def run(self):
        if os.environ.get("TESTING_LAI"):
            print(
                "this is a simple Lightning app to verify your component is working as expected"
            )
        self.slack_command_bot.run()


if __name__ == "__main__":
    app = L.LightningApp(LitApp())
