import time, re
from slackclient import SlackClient
from config import *

sc = SlackClient(SLACK_BOT_TOKEN)
sc_id = None
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
delay = 1


def read_command(slack_events):

    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = mentioned(event["text"])
            if user_id == sc_id:
                return message, event['channel']
    return None, None


def mentioned(message):

    matches = re.search(MENTION_REGEX, message)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):

    default_response = "I don't know what you mean"
    response = None
    if command.startswith('post'):
        response = "twitter response"

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == '__main__':
    if sc.rtm_connect(with_team_state=False):
        print "SLACK BOT is now online"
        sc_id = sc.api_call("auth.test")["user_id"]
        while True:
            command, channel = read_command(sc.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(delay)
    else:
        print "Failed Connection"

