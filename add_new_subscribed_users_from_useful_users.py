import argparse

import configure
from User import me
from insta_browser import browser

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='enable debug mode', action="store_true")
parser.add_argument('--count', help='number of useful users to use', type=int)
args = parser.parse_args()
debug = args.debug
count = args.count if args.count is not None and args.count < len(me.get_list_of_useful_usernames()) else len(
    me.get_list_of_useful_usernames())

login = me.get_login()
password = me.get_password()

br = browser.Browser(
    debug=debug,
    cookie_path=configure.COOKIE_PATH,
    log_path=configure.LOG_PATH,
    db_path=configure.DB_PATH,
)

try:
    list_of_useful_usernames = me.get_list_of_useful_usernames()
    br.logger.log("Parsing {} users.".format(len(list_of_useful_usernames)))
    br.auth(login, password)
    for i in range(count):
        br.get_subscribed_of_username(list_of_useful_usernames[i])
        br.logger.log('----------------')
finally:
    br.close_all()
