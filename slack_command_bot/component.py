import os
from functools import partial

import lightning as L
import slack
from dotenv import load_dotenv
from flask import Flask, request
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore
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

    def __init__(
        self,
        command="/",
        signing_secret=None,
        bot_token=None,
        slack_client_id=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.command = command
        if not signing_secret:
            signing_secret = os.environ["SIGNING_SECRET"]
        if not bot_token:
            bot_token = os.environ["BOT_TOKEN"]
        self.slack_client_id = slack_client_id or os.environ["SLACK_CLIENT_ID"]
        self.signing_secret = signing_secret
        self.bot_token = bot_token

    def handle_command(self):
        """Cutomize this method the way you want your bot to interact with the prompt."""
        client = slack.WebClient(token=self.bot_token)
        data: dict = request.form
        import pyjokes

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

        create_oauth_url(flask_app=flask_app, slack_client_id=self.slack_client_id)

        flask_app.route(self.command, methods=["POST", "GET"])(self.handle_command)
        print("starting Slack Command Bot")
        flask_app.run(host=self.host, port=self.port)


def create_oauth_url(flask_app, slack_client_id):

    # Issue and consume state parameter value on the server-side.
    state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")
    # Persist installation data and lookup it by IDs.
    installation_store = FileInstallationStore(base_dir="./data")

    # Build https://slack.com/oauth/v2/authorize with sufficient query parameters
    authorize_url_generator = AuthorizeUrlGenerator(
        client_id=slack_client_id,
        scopes=["chat:write", "chat:write.public", "commands", "files:write"],
    )

    @flask_app.route("/slack/install", methods=["GET"])
    def oauth_start():
        # Generate a random value and store it on the server-side
        state = state_store.issue()
        # https://slack.com/oauth/v2/authorize?state=(generated value)&client_id={client_id}&scope=app_mentions:read,chat:write&user_scope=search:read
        url = authorize_url_generator.generate(state)
        return (
            f'<a href="{url}">'
            f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'
        )
