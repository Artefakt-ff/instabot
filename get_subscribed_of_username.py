# -*- coding: utf-8 -*-
import argparse
import os

from User import me
from insta_browser import browser
import configure

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='enable debug mode', action="store_true")
parser.add_argument('--force_update', help='force updating of user\'s subscription', action="store_true")
parser.add_argument('--username', help='if indicated, like posts by count', type=str, required=True)
args = parser.parse_args()
debug = args.debug
username = args.username
force_update = args.force_update

login = me.get_login()
password = me.get_password()

br = browser.Browser(
    debug=debug,
    cookie_path=configure.COOKIE_PATH,
    log_path=configure.LOG_PATH,
    db_path=configure.DB_PATH,
)

try:
    if not force_update and os.path.isfile('users_subscribers/' + username + '.json'):
        br.logger.log('Able to use cached list.')
    else:
        br.logger.log("Can\'t find cached list or subscribers or used option \'force_update\'")
        br.auth(login, password)
        br.get_subscribed_of_username(username)
finally:
    br.close_all()
