#!/usr/bin/env python
# encoding: utf-8
"""
A random report from the ten years' worth of official reports about decapitated
animals discovered in New York City public parks.

Data: http://uselesspress.org/things/decapitated-animals-dataset/
"""
from __future__ import print_function
import argparse
import json
import random
import re
import sys
import twitter
import webbrowser
import yaml


REGEX = re.compile('[^a-zA-Z0-9]')


# cmd.exe cannot do Unicode so encode first
def print_it(text):
    print(text.encode('utf-8'))


def load_yaml(filename):
    """
    File should contain:
    consumer_key: TODO_ENTER_YOURS
    consumer_secret: TODO_ENTER_YOURS
    access_token: TODO_ENTER_YOURS
    access_token_secret: TODO_ENTER_YOURS
    """
    f = open(filename)
    data = yaml.safe_load(f)
    f.close()
    if not data.viewkeys() >= {
            'access_token', 'access_token_secret',
            'consumer_key', 'consumer_secret'}:
        sys.exit("Twitter credentials missing from YAML: " + filename)
    return data


def tweet_it(string, coords, credentials):
    """ Tweet string using credentials """
    if len(string) <= 0:
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file
    t = twitter.Twitter(auth=twitter.OAuth(
        credentials['access_token'],
        credentials['access_token_secret'],
        credentials['consumer_key'],
        credentials['consumer_secret']))

    print_it("TWEETING THIS:\n" + string)

    (latitude, longitude) = coords

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        result = t.statuses.update(
            status=string,
            lat=latitude, long=longitude,
            display_coordinates=True)
        url = "http://twitter.com/" + \
            result['user']['screen_name'] + "/status/" + result['id_str']
        print("Tweeted:\n" + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


def only_alphanumeric(text):
    """ Only allow alphanumeric chars in text """
    return REGEX.sub("", text)


def insert_into_text(insertable, text, index):
    """ Insert insertable into text at index """
    return text[:index] + insertable + text[index:]


def insert_hashtag(text, tag):
    """ If tag in text, make first one a hashtag """
    for tag2 in [tag, tag.lower(), tag.upper()]:
        pos = text.find(tag2)
        if pos >= 0:
            text = insert_into_text("#", text, pos)
            break
    return text


def nychickens(infile):
    """ Main bit """
    with open(infile) as data_file:
        data = json.load(data_file)

    report = random.choice(data)

    tags = report['animal'].split()
    complaint = report['complaint_details']
    for tag in tags:
        tag = only_alphanumeric(tag)
        complaint = insert_hashtag(complaint, tag)

    tweet = (
        complaint + "/" +
        report['additional_location_details'] + "/" +
        report['park_or_facility'] + "/" +
        report['site_city_zip']
        )

    if len(tweet) > 140:
        tweet = tweet[:139].strip() + u"…"

    coords = (report['lat'], report['lng'])
    print(coords)
    return tweet, coords


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A random report from the ten years' worth of official "
                    "reports about decapitated animals discovered in "
                    "New York City public parks.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-i', '--infile',
        default='/Users/hugo/Dropbox/bin/data/animals.json',
        help="Input data file")
    parser.add_argument(
        '-y', '--yaml',
        default='/Users/hugo/Dropbox/bin/data/nychickens.yaml',
        help="YAML file location containing Twitter keys and secrets")
    parser.add_argument(
        '-nw', '--no-web', action='store_true',
        help="Don't open a web browser to show the tweeted tweet")
    parser.add_argument(
        '-c', '--chance',
        type=int, default=4,
        help="Denominator for the chance of tweeting this time")
    parser.add_argument(
        '-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't tweet anything")
    args = parser.parse_args()

    # Do we have a chance of tweeting this time?
    if random.randrange(args.chance) > 0:
        sys.exit("No tweet this time")

    credentials = load_yaml(args.yaml)

    tweet, coords = nychickens(args.infile)

    tweet_it(tweet, coords, credentials)

# End of file
