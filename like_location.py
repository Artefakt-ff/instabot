# -*- coding: utf-8 -*-
import argparse

import configure
from User import me
from insta_browser import browser

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='enable debug mode', action="store_true")
parser.add_argument('--auto_follow', help='Enable auto following', action="store_true")
parser.add_argument('--count', help='if indicated, like posts by count', type=int, default=None)
parser.add_argument('--location', help='if indicated, like posts by count', type=str, required=True)
args = parser.parse_args()
debug = args.debug
count = args.count
auto_follow = args.auto_follow
location = args.location

login = me.get_login()
password = me.get_password()

br = browser.Browser(
    debug=debug,
    cookie_path=configure.COOKIE_PATH,
    log_path=configure.LOG_PATH,
    db_path=configure.DB_PATH,
    exclude=configure.exclude,
    auto_follow=auto_follow
)
try:
    br.auth(login, password)
    br.process_location(location, count)
    print(br.get_summary())
finally:
    br.close_all()
