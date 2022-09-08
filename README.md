# slack_command_bot component

<img src="https://i.ibb.co/KL4ML46/slack-bot.jpg">

With this app you can create a Slack bot and enable interactivity with the Slash Commands.
It can recieve slash commands and send message or files with the Slack client API.

## To run slack_command_bot

First, install slack_command_bot (warning: this component has not been officially approved on the lightning gallery):

```bash
lightning install component https://github.com/Lightning-AI/slack_command_bot
```

Once the app is installed, use it in an app:

```python
from slack_command_bot import SlackCommandBot
import lightning as L
import slack
from flask import request


class DemoSlackCommandBot(SlackCommandBot):
    def handle_command(self):
        """Cutomize this method the way you want your bot to interact with the prompt."""
        client = slack.WebClient(token=self.bot_token)
        data: dict = request.form
        channel_id = data["channel_id"]

        client.chat_postMessage(text="testing post msg", channel=channel_id)
        return "Hey there! command was received successfully", 200


class LitApp(L.LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.slack_bot = DemoSlackCommandBot(command="/LAIcommand")

    def run(self):
        print(
            "this is a simple Lightning app to verify your component is working as expected"
        )
        self.slack_bot.run()


app = L.LightningApp(LitApp())
```
