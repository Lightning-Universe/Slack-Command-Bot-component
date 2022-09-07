r"""To test a lightning component:

1. Init the component.
2. call .run()
"""
from slack_command_bot import SlackCommandBot


def test_placeholder_component():
    messenger = SlackCommandBot()
    messenger.run()
    assert messenger.value == 1
