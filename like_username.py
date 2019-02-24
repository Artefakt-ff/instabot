# -*- coding: utf-8 -*-
import argparse

import configure
from User import me
from insta_browser import browser

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='enable debug mode', action="store_true")
parser.add_argument('--count', help='if indicated, like posts by count', type=int, default=None)
parser.add_argument('--username', help='if indicated, like posts by count', type=str, required=True)
args = parser.parse_args()
debug = args.debug
count = args.count
username = args.username

login = me.get_login()
password = me.get_password()

br = browser.Browser(
    debug=debug,
    cookie_path=configure.COOKIE_PATH,
    log_path=configure.LOG_PATH,
    db_path=configure.DB_PATH,
)
try:
    br.auth(login, password)
    br.process_user(username, count)
    print(br.get_summary())
finally:
    br.close_all()
