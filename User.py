import json
import time
from json import JSONDecodeError


class User:
    MAX_SUBSCRIBE_LIMIT = 59
    MIN_TIME_TO_NEW_SUBSCRIPTIONS = 60 * 60
    TTL_OF_SUBSCRIPTION = 3 * 24 * 60 * 60 * 60

    def __init__(self, login='', password=''):
        # TODO: Сделай проверку пути
        self.login = login
        self.password = password
        self.dict_of_subscribers_file = '../user_data/' + login + '_subscribers.json'
        self.configuration_file = '../user_data/' + login + '_configuration.json'

    def __str__(self):
        return self.login

    def get_login(self):
        return self.login

    def get_password(self):
        return self.password

    def get_subscribers(self, format_of_return='dict'):
        with open(self.dict_of_subscribers_file, 'r') as fp:
            list_of_subscribers = json.load(fp)
        if format_of_return == 'dict':
            return list_of_subscribers
        return list(list_of_subscribers.keys())

    def update_dict_of_subscribers(self, data):
        try:
            with open(self.dict_of_subscribers_file, 'r') as fp:
                dict_of_subscribers = json.load(fp)
            for user, date_of_subscription in data.items():
                dict_of_subscribers[user] = date_of_subscription
            with open(self.dict_of_subscribers_file, 'w') as fp:
                json.dump(dict_of_subscribers, fp)
            return True
        except JSONDecodeError:
            return False

    def is_subscribed(self, username) -> bool:
        if username in self.get_subscribers(format_of_return='list'):
            return True
        return False

    def add_subscribed_username(self, username):
        with open(self.dict_of_subscribers_file, 'r', encoding='utf8', errors='ignore') as fp:
            dict_of_subscribers = json.load(fp)
        dict_of_subscribers[username] = time.time()
        self.update_time_of_last_subscription()
        with open(self.dict_of_subscribers_file, 'w', encoding='utf8', errors='ignore') as fp:
            json.dump(dict_of_subscribers, fp)
        return True

    def delete_unsubscribed_username(self, username) -> bool:
        with open(self.dict_of_subscribers_file, 'r', encoding='utf8', errors='ignore') as fp:
            dict_of_subscribers = json.load(fp)
        if dict_of_subscribers.pop(username, None) is None:
            return False
        with open(self.dict_of_subscribers_file, 'w', encoding='utf8', errors='ignore') as fp:
            json.dump(dict_of_subscribers, fp)
        return True

    def can_subscribe_on_new_user(self) -> bool:
        with open(self.configuration_file, 'r', encoding='utf8', errors='ignore') as fp:
            dict_of_configuration = json.load(fp)
        if time.time() - dict_of_configuration['time_of_last_subscription'] > self.MIN_TIME_TO_NEW_SUBSCRIPTIONS:
            return True
        return False

    def update_time_of_last_subscription(self):
        with open(self.configuration_file, 'r', encoding='utf8', errors='ignore') as fp:
            dict_of_configuration = json.load(fp)
        dict_of_configuration['time_of_last_subscription'] = time.time()
        with open(self.configuration_file, 'w', encoding='utf8', errors='ignore') as fp:
            json.dump(dict_of_configuration, fp)

    def get_list_of_useful_usernames(self) -> list:
        with open(self.configuration_file, 'r', encoding='utf8', errors='ignore') as fp:
            list_of_useful_usernames = json.load(fp)['useful_usernames']
        return list_of_useful_usernames

    def extend_list_of_useful_usernames(self, data):
        with open(self.configuration_file, 'r', encoding='utf8', errors='ignore') as fp:
            dict_of_configuration = json.load(fp)
        dict_of_configuration['useful_usernames'].extend(list(
            set(data).difference(
                set(dict_of_configuration['useful_usernames'])))) # finding usernames that don't repeating
        with open(self.configuration_file, 'w', encoding='utf8', errors='ignore') as fp:
            json.dump(dict_of_configuration, fp)

    def get_list_of_possible_unsubscriptions(self):
        dict_of_subscriptions = self.get_subscribers(format_of_return='dict')
        list_of_possible_unsubscriptions = []
        for user, time_of_subscription in dict_of_subscriptions.items():
            if time.time() - time_of_subscription > self.TTL_OF_SUBSCRIPTION:
                list_of_possible_unsubscriptions.append(user)
        return list_of_possible_unsubscriptions


me = User()
