import json
import os

import lightning as L
import requests
import slack
from flask import request

from slack_command_bot import SlackCommandBot


class DemoSlackCommandBot(SlackCommandBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.API_URL = os.environ("SHEET_API_URL")

    def save_new_workspace(self, team_id, bot_token):
        data = [{"team_id": team_id, "bot_token": bot_token}]
        data = json.dumps(data)

        response = requests.post(self.API_URL, data=data)
        response.raise_for_status()

    def handle_command(self):
        """Cutomize this method the way you want your bot to interact with the command."""

        data: dict = request.form
        team_id = data["team_id"]
        response = requests.get(
            f"{self.API_URL}?search=" + json.dumps({"team_id": team_id})
        )
        bot_token = response.json()[0]["bot_token"]

        client = slack.WebClient(token=bot_token)
        client.chat_postMessage(channel=data.get("channel_id"), text="Testing send msg")
        return "Hey there! command was received successfully", 200


class LitApp(L.LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.slack_command_bot = DemoSlackCommandBot()

    def run(self):
        # print(
        #     "this is a simple Lightning app to verify your component is working as expected"
        # )
        self.slack_command_bot.run()


if __name__ == "__main__":
    app = L.LightningApp(LitApp(), debug=True)
