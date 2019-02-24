# -*- coding: utf-8 -*-
import json

from selenium import webdriver

from User import me
from .logger import Logger
from .auth import *
from .processors.not_feed_processor import *
from .processors.feed_processor import *
from .db.browser_db import BrowserDB
import re


class Browser:
    login = ''
    summary = {}

    """
    :param chrome: is deprecated and will be removed in future versions
    """

    def __init__(self, debug=False, chrome=False, cookie_path=None, log_path=None, db_path=None,
                 exclude=None, auto_follow=False):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--window-size=900,768')
        self.browser = webdriver.Chrome('chromedriver.exe')
        self.browser.implicitly_wait(10)

        self.cookie_path = cookie_path
        self.exclude = exclude or []
        self.chrome = chrome
        self.logger = Logger(log_path, debug)
        self.db = BrowserDB(self.logger, db_path)
        self.auto_follow = auto_follow

    def auth(self, login, password):
        if not login:
            raise ValueError('Please provide login and password for Browser.auth method')
        self.db.detect_account(login)
        br = self.browser
        self.get("https://www.instagram.com/accounts/login/")
        time.sleep(1)
        if not auth_with_cookies(br, self.logger, login, self.cookie_path):
            auth_with_credentials(br, self.logger, login, password, self.cookie_path)
        self.login = login

    def get(self, url):
        self.browser.get(url)
        time.sleep(.5)
        self.logger.log(u'Open ' + self.browser.current_url)
        return self

    def close_all(self):
        self.logger.save_screen_shot(self.browser, 'exit.png')
        self.browser.close()
        self.browser.quit()
        self.logger.log(u'Browser process was ended')
        self.logger.log(u'')



    def get_summary(self):
        log = 'Feed scrolled down {scrolled} times, liked {liked} posts, skipped {skipped} posts,' \
              ' skipped excluded {excluded} posts'. \
            format(**self.summary)
        self.logger.log_to_file(log)
        return log

    def process_user(self, username, count=None):
        br = self.browser
        self.get("https://www.instagram.com/{}".format(username))
        self.logger.log("Start liking @{} profile {} posts".format(username, count))
        processor = NotFeedProcessor(db=self.db, br=br, lg=self.logger)
        processor.set_auto_follow(self.auto_follow)
        processor.like_user_profile(count)
        self.summary = processor.get_summary()

    def process_location(self, location, count=None):
        br = self.browser
        processed_location = re.sub('^(/?explore/locations/|/|/?locations/)', '', location)
        self.get("https://www.instagram.com/explore/locations/{}".format(processed_location))
        self.logger.log("Start liking top posts from {} location".format(processed_location))
        processor = NotFeedProcessor(db=self.db, br=br, lg=self.logger)
        processor.set_auto_follow(self.auto_follow)
        processor.like_top()
        processor.like_latest(count)
        self.summary = processor.get_summary()

    def process_tag(self, tag, count=None):
        br = self.browser
        self.get("https://www.instagram.com/explore/tags/{}".format(tag))
        self.logger.log("Start liking top posts from #{} tag".format(tag))
        processor = NotFeedProcessor(db=self.db, br=br, lg=self.logger)
        processor.set_auto_follow(self.auto_follow)
        processor.like_top()
        processor.like_latest(count)
        self.summary = processor.get_summary()

    def process_feed(self, count=None):
        br = self.browser
        self.get("https://instagram.com/")
        time.sleep(.5)
        processor = FeedProcessor(db=self.db, br=br, lg=self.logger)
        processor.set_auto_follow(self.auto_follow)
        processor.scroll_feed_to_last_not_liked_posts(count)
        processor.process(self.exclude, self.login)
        self.summary = processor.get_summary()

    def subscribe_username(self, username):
        br = self.browser
        self.get("https://www.instagram.com/{}".format(username))
        self.logger.log("Subscribing on {}".format(username))
        processor = BaseProcessor(db=self.db, br=br, lg=self.logger)
        processor.subscribe_username(username)
        self.summary = processor.get_summary()

    def unsubscribe_username(self, username):
        br = self.browser
        self.get("https://www.instagram.com/{}".format(username))
        self.logger.log("Unsubscribing from {}".format(username))
        processor = BaseProcessor(db=self.db, br=br, lg=self.logger)
        processor.unsubscribe_username(username)
        self.summary = processor.get_summary()

    def get_subscribers_of_username(self, username):
        br = self.browser
        self.get("https://www.instagram.com/{}".format(username))
        self.logger.log("Check list of subscribers of {}.".format(username))
        processor = BaseProcessor(db=self.db, br=br, lg=self.logger)
        processor.get_list_of_subscribers(username)
        self.summary = processor.get_summary()

    def subscribe_on_new_users(self, username, count):
        br = self.browser
        self.logger.log("Check list of subscribers of {}.".format(username))
        self.get_subscribers_of_username(username)
        with open('../users_subscribers/'+username+'.json', 'r', encoding='utf8', errors='ignore') as fp:
            list_of_future_subscribers = json.load(fp)
        length_list_of_subscribers = len(list_of_future_subscribers)

        for i in range(count):
            try:
                self.subscribe_username(list_of_future_subscribers[length_list_of_subscribers-i])
                list_of_future_subscribers.pop()
                me.add_subscribed_username(username)
            except Exception as e:
                self.logger.log('Something went wrong. Code of error: {}.'.format(str(e)))

        with open('..users_subscribers/' + username + '.json', 'w', encoding='utf8', errors='ignore') as fp:
            json.dump(list_of_future_subscribers, fp)


