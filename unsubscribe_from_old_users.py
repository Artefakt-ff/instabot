import argparse
import time

import configure
from User import me
from insta_browser import browser

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='enable debug mode', action="store_true")
args = parser.parse_args()
debug = args.debug

login = me.get_login()
password = me.get_password()

list_of_possible_unsubscriptions = me.get_list_of_possible_unsubscriptions()
if len(list_of_possible_unsubscriptions):

    br = browser.Browser(
        debug=debug,
        cookie_path=configure.COOKIE_PATH,
        log_path=configure.LOG_PATH,
        db_path=configure.DB_PATH,
    )
    br.logger.log('Can unsubscribe from {} users.'.format(len(list_of_possible_unsubscriptions)))
    br.auth(login, password)
    for user in list_of_possible_unsubscriptions:
        br.unsubscribe_username(user)
    br.close_all()
else:
    print('No user users to unsubscribe.')
