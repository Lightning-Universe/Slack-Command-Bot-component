import lightning as L

from slack_command_bot import SlackCommandBot


class LitApp(L.LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.slack_command_bot = SlackCommandBot()

    def run(self):
        print(
            "this is a simple Lightning app to verify your component is working as expected"
        )
        self.slack_command_bot.run()


app = L.LightningApp(LitApp())
