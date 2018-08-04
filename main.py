import time, re, tweepy, json, datetime, schedule
from slackclient import SlackClient
from config import *

sc = SlackClient(SLACK_BOT_TOKEN)
sc_id = None
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
LOCATION_ID = 1187115


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
    isauto = False
    if command.startswith('post'):
        response = trending(channel, isauto)

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def trending(channel='assignment1', isauto=True):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    twitter = tweepy.API(auth)
    now = datetime.datetime.now()
    top10 = []

    """ get trend and put it in a list """
    trends = json.loads(json.dumps(twitter.trends_place(LOCATION_ID), indent=1))
    opening_response = 'Here are the Top Trending now (%s %d, %d)' % (now.strftime('%B'), now.day, now.year)
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=opening_response
    )

    count = 0
    for trend in trends[0]['trends']:
        if count < 10:
            top10.append("%d) %s" % (count + 1, trend["name"]))
            count += 1
        else:
            break

    if isauto:
        response = ' \n'.join(top10)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=response
        )

    else:
        return ' \n'.join(top10)


def delay(delay=1):
    return time.sleep(delay)


""" main function of the slackbot script"""
if __name__ == '__main__':
    if sc.rtm_connect(with_team_state=False):
        print "SLACK BOT is now online"
        sc_id = sc.api_call("auth.test")["user_id"]
        schedule.every().day.at('10:30').do(trending)
        # schedule.every().hour.do(trending)
        # schedule.every().minute.do(trending)
        while True:
            schedule.run_pending()
            delay()
            command, channel = read_command(sc.rtm_read())
            if command:
                handle_command(command, channel)
            delay()
    else:
        print "Failed Connection"

