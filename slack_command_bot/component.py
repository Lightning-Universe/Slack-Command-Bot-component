import os
from functools import partial

import lightning as L
import pyjokes
import slack
from dotenv import load_dotenv
from flask import Flask, request
from slackeventsapi import SlackEventAdapter

load_dotenv(".env")


class SlackCommandBot(L.LightningWork):
    """
    With this app you can create a Slack bot and enable interactivity with the Slash Commands.
    It can recieve slash commands and send message or files with the Slack client API.

    To run this components:

    Step 1: Create a Slack App by logging in to https://api.slack.com

    Step 2: Copy the "bot token" and "signing token" from Slack App settings

    Step 3: Cutomize the handle_command method the way you want your bot to interact with the prompt.


    class SlackRootFlow(L.LightningFlow):
        def __init__(self):
            super().__init__()
            self.slack_bot = SlackCommandBot(bot_token, signing_secret)

        def run(self):
            self.slack_bot.run()
    """

    def __init__(self, signing_secret=None, bot_token=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not signing_secret:
            signing_secret = os.environ["SIGNING_SECRET"]
        if not bot_token:
            bot_token = os.environ["BOT_TOKEN"]
        self.signing_secret = signing_secret
        self.bot_token = bot_token

    def handle_command(self, client: slack.WebClient):
        """Cutomize this method the way you want your bot to interact with the prompt."""
        data: dict = request.form

        client.chat_postMessage(pyjokes.get_joke())
        return "Hey there! prompt was recieved successfully", 200

    def run(self, *args, **kwargs) -> None:
        flask_app = Flask(__name__)
        client = slack.WebClient(token=self.bot_token)
        slack_events_adapter = SlackEventAdapter(
            self.signing_secret, "/slack/events", flask_app
        )
        BOT_ID = client.api_call("auth.test")["user_id"]
        print(f"Bot initialized with id: {BOT_ID}")

        flask_app.route(partial(self.handle_command, client), methods=["POST", "GET"])
        print("starting Slack Command Bot")
        flask_app.run(host=self.host, port=self.port)
