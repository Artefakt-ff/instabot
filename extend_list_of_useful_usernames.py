import argparse

import configure
from User import me
from insta_browser import browser

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='enable debug mode', action="store_true")
parser.add_argument('--file', help='path to specific file with new useful_users', type=str)
args = parser.parse_args()
debug = args.debug
file = args.file or "new_useful_users.txt"


try:
    with open(file, 'r', encoding='utf8', errors='ignore') as fp:
        lines = fp.readlines()
    used_users = [line for line in lines if line[0] == '#']
    formatted_users = [line.strip() for line in lines if line[0] != '#']
    if formatted_users:
        print("Found {} users.".format(len(formatted_users)))
        me.extend_list_of_useful_usernames(formatted_users)
        formatted_users = ['# used ' + formatted_user + '\n' for formatted_user in formatted_users]
        with open(file, 'w', encoding='utf8', errors='ignore') as fp:
            fp.writelines(used_users)
            fp.writelines(formatted_users)
        print('Successfully add new useful users.')
    else:
        print("No new users for adding.")
except FileNotFoundError:
    print('Wrong path to file.')

input()