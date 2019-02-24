import argparse
import json

import configure
from User import me
from insta_browser import browser

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='enable debug mode', action="store_true")
parser.add_argument('--count', help='number of users to subscribe', type=int)
args = parser.parse_args()
debug = args.debug
count = args.count or me.MAX_SUBSCRIBE_LIMIT

login = me.get_login()
password = me.get_password()

if me.can_subscribe_on_new_user():
    list_of_useful_usernames = me.get_list_of_useful_usernames()

    if list_of_useful_usernames:
        list_of_future_subscribers = []
        i = 0

        for useful_username in list_of_useful_usernames:
            is_file_ended = True

            with open('../users_subscribers/' + useful_username + '.json', 'r', encoding='utf8', errors='ignore') as fp:
                list_of_username_subscriptions = json.load(fp)
            length_of_list = len(list_of_username_subscriptions)
            if length_of_list:
                for j in range(length_of_list):
                    list_of_future_subscribers.append(list_of_username_subscriptions[length_of_list-j-1])
                    list_of_username_subscriptions.pop()
                    i += 1
                    if i == count:
                        with open('users_subscribers/' + useful_username + '.json', 'w', encoding='utf8',
                                  errors='ignore') as fp:
                            json.dump(list_of_future_subscribers, fp)
                        if j < length_of_list:
                            is_file_ended = False
                        break
            with open('users_subscribers/' + useful_username + '.json', 'w', encoding='utf8',
                      errors='ignore') as fp:
                json.dump([], fp)

            if i == count:
                break
            print(list_of_future_subscribers)
        if list_of_future_subscribers:
            br = browser.Browser(
                debug=debug,
                cookie_path=configure.COOKIE_PATH,
                log_path=configure.LOG_PATH,
                db_path=configure.DB_PATH,
            )
            br.auth(login, password)
            br.logger.log('Can subscribe on {} users.'.format(len(list_of_future_subscribers)))
            br.logger.log('Subscribing...')
            for user in list_of_future_subscribers:
                br.subscribe_username(user)
            br.close_all()
        else:
            print('No available subscribers. Use extend_list_of_useful_usernames.py to add new sources.')
    else:
        print("No sources for subscription. Use extend_list_of_useful_usernames.py to add new sources.")
else:
    print('Did not have enough time to new subscriptions. Try later.')
