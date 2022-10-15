import abc
import os

import lightning as L
import slack
from dotenv import load_dotenv
from flask import Flask, make_response, redirect, request
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slackeventsapi import SlackEventAdapter

load_dotenv(".env")


# TODO: @aniketmaurya cleanup the oauth code


class SlackCommandBot(L.LightningWork):
    """With this app you can create a Slack bot and enable interactivity with the Slash Commands. It can recieve slash
    commands and send message or files with the Slack client API.

    To run this components:

    Step 1: Create a Slack App by logging in to https://api.slack.com

    Step 2: Copy the "bot token", "signing token", "CLIENT SECRET", CLIENT ID from Slack App settings.

    Step 3: Cutomize the handle_command method the way you want your bot to interact with the prompt.


    How to make this app publicly distributable:

    Step 1: Launch this app and copy the url for the Slack Bot Work (let's say this BOT_URL).
    Step 2: Add Redirect URL on Slack API settings as https://BOT_URL/slack/oauth/callback
    Step 3: To install the app can use the "Add to Slack" button at https://BOT_URL/slack/install
    Step 4: After the installation, you will have to launch the Lightning App with tokens for the newly created Slack app.


    class SlackRootFlow(L.LightningFlow):
        def __init__(self):
            super().__init__()
            self.slack_bot = SlackCommandBot()

        def run(self):
            self.slack_bot.run()
    """

    def __init__(
        self,
        command="/lai",
        signing_secret=None,
        bot_token=None,
        slack_client_id=None,
        client_secret=None,
        *args,
        **kwargs,
    ):
        super().__init__(parallel=True, *args, **kwargs)
        self.command = command

        self._slack_client_id = slack_client_id or os.environ.get("SLACK_CLIENT_ID")
        self._client_secret = client_secret or os.environ.get("CLIENT_SECRET")
        self._signing_secret = signing_secret or os.environ.get("SIGNING_SECRET")
        self._bot_token = bot_token or os.environ.get("BOT_TOKEN")

    @abc.abstractmethod
    def handle_command(self):
        """Customize this method the way you want your bot to interact with the prompt.

        See the example in app.py
        """

    def save_new_workspace(self, team_id, bot_token):
        """Implement this method to save the team id and bot token for distributing slack workspace."""

    @property
    def bot_token(self):
        return self._bot_token

    def init_flask_app(self, app: Flask = None):
        if not app:
            app = Flask(__name__)

        client = slack.WebClient(token=self._bot_token)
        SlackEventAdapter(self._signing_secret, "/slack/events", app)
        BOT_ID = client.api_call("auth.test")["user_id"]
        print(f"Bot initialized with id: {BOT_ID}")

        # Issue and consume state parameter value on the server-side.
        state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")
        # Persist installation data and lookup it by IDs.
        installation_store = FileInstallationStore(base_dir="./data")

        # Build https://slack.com/oauth/v2/authorize with sufficient query parameters
        authorize_url_generator = AuthorizeUrlGenerator(
            client_id=self._slack_client_id,
            scopes=[
                "chat:write",
                "chat:write.public",
                "commands",
                "files:write",
                "incoming-webhook",
            ],
        )

        self._create_oauth_url(
            flask_app=app,
            slack_client_id=self._slack_client_id,
            state_store=state_store,
            authorize_url_generator=authorize_url_generator,
            installation_store=installation_store,
        )
        self._create_redirect_url(
            flask_app=app,
            slack_client_id=self._slack_client_id,
            client_secret=self._client_secret,
            state_store=state_store,
            installation_store=installation_store,
        )
        app.route(self.command, methods=["POST", "GET"])(self.handle_command)

    def run(self, *args, **kwargs) -> None:
        app = Flask(__name__)
        self.init_flask_app(app=app)
        print("starting Slack Command Bot")
        app.run(host=self.host, port=self.port)

    def _create_oauth_url(
        self,
        flask_app,
        slack_client_id,
        state_store,
        authorize_url_generator,
        installation_store,
    ):
        @flask_app.route("/slack/install", methods=["GET"])
        def oauth_install():
            # Generate a random value and store it on the server-side
            state = state_store.issue()
            # https://slack.com/oauth/v2/authorize?state=(generated value)&client_id={client_id}&scope=app_mentions:read,chat:write&user_scope=search:read
            url = authorize_url_generator.generate(state)
            return (
                f'<a href="{url}">'
                f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'
            )

        @flask_app.route("/slack/start", methods=["GET"])
        def oauth_start():
            # Generate a random value and store it on the server-side
            state = state_store.issue()
            # https://slack.com/oauth/v2/authorize?state=(generated value)&client_id={client_id}&scope=app_mentions:read,chat:write&user_scope=search:read
            url = authorize_url_generator.generate(state)
            return redirect(url)

    def _create_redirect_url(
        self, flask_app, slack_client_id, client_secret, state_store, installation_store
    ):
        # Redirect URL
        @flask_app.route("/slack/oauth/callback", methods=["GET"])
        def oauth_callback():
            # Retrieve the auth code and state from the request params
            if "code" in request.args:
                # Verify the state parameter
                if state_store.consume(request.args["state"]):
                    client = slack.WebClient()  # no prepared token needed for this
                    # Complete the installation by calling oauth.v2.access API method
                    oauth_response = client.oauth_v2_access(
                        client_id=slack_client_id,
                        client_secret=client_secret,
                        # redirect_uri=redirect_uri,
                        code=request.args["code"],
                    )

                    installed_enterprise = oauth_response.get("enterprise", {}) or {}
                    is_enterprise_install = oauth_response.get("is_enterprise_install")
                    installed_team = oauth_response.get("team", {})
                    installer = oauth_response.get("authed_user", {})
                    incoming_webhook = oauth_response.get("incoming_webhook", {})

                    bot_token = oauth_response.get("access_token")
                    # NOTE: oauth.v2.access doesn't include bot_id in response
                    bot_id = None
                    enterprise_url = None
                    if bot_token is not None:
                        auth_test = client.auth_test(token=bot_token)
                        bot_id = auth_test["bot_id"]
                        if is_enterprise_install is True:
                            enterprise_url = auth_test.get("url")

                    installation = Installation(
                        app_id=oauth_response.get("app_id"),
                        enterprise_id=installed_enterprise.get("id"),
                        enterprise_name=installed_enterprise.get("name"),
                        enterprise_url=enterprise_url,
                        team_id=installed_team.get("id"),
                        team_name=installed_team.get("name"),
                        bot_token=bot_token,
                        bot_id=bot_id,
                        bot_user_id=oauth_response.get("bot_user_id"),
                        bot_scopes=oauth_response.get(
                            "scope"
                        ),  # comma-separated string
                        user_id=installer.get("id"),
                        user_token=installer.get("access_token"),
                        user_scopes=installer.get("scope"),  # comma-separated string
                        incoming_webhook_url=incoming_webhook.get("url"),
                        incoming_webhook_channel=incoming_webhook.get("channel"),
                        incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                        incoming_webhook_configuration_url=incoming_webhook.get(
                            "configuration_url"
                        ),
                        is_enterprise_install=is_enterprise_install,
                        token_type=oauth_response.get("token_type"),
                    )

                    self.save_new_workspace(
                        team_id=installed_team.get("id"), bot_token=bot_token
                    )

                    # Store the installation
                    installation_store.save(installation)

                    return f"<h1>Thanks for installing this app! Add the bot user to a channel and try the command `/{self.command}`</h1>"
                else:
                    return make_response(
                        f"Try the installation again (the state value is already expired)",
                        400,
                    )

            error = request.args["error"] if "error" in request.args else ""
            return make_response(
                f"Something is wrong with the installation (error: {error})", 400
            )
