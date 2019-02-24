import datetime
import json
import os
import time

import selenium.common.exceptions as excp
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from User import me


def write_subscribers_of_username_to_file(username, list_of_subscribers):
    # TODO: Сделай проверку пути
    with open('../users_subscribers/' + username + '.json', 'w', encoding='utf8') as fp:
        json.dump(list_of_subscribers, fp)
    return True


class BaseProcessor:
    post_skipped_excluded = 0
    posts_count_to_like = 0
    feed_scrolled_down = 0
    post_already_liked = 0
    post_excluded = 0
    post_skipped = 0
    auto_follow = False
    like_limit = 416
    progress = None
    post_liked = 0
    heart = None
    count = 0
    hour_like_limit = 150

    def __init__(self, db, br, lg):
        self.db = db
        self.browser = br
        self.logger = lg

    def get_summary(self):
        return {'liked': self.post_liked,
                'skipped': self.post_skipped,
                'excluded': self.post_skipped_excluded,
                'already_liked': self.post_already_liked,
                'scrolled': self.feed_scrolled_down}

    @staticmethod
    def _get_feed_post_link(post: WebElement):
        """
        Get link to post from post web-element from feed
        :param post: WebElement
        :return:
        """
        try:
            post_link = post.find_element_by_css_selector('div:nth-child(3) div:nth-child(4) a')
        except excp.NoSuchElementException:
            post_link = post.find_element_by_css_selector('div:nth-child(3) div:nth-child(3) a')
        return post_link.get_attribute('href')

    @staticmethod
    def _get_feed_post_media(post: WebElement):
        """
        Get link to post from post web-element from feed
        :param post: WebElement
        :return: str
        """
        try:
            image = post.find_element_by_css_selector('div:nth-child(2) img')
            return image.get_attribute('src')
        except excp.NoSuchElementException:
            pass

        try:
            video = post.find_element_by_tag_name('video')
            return video.get_attribute('src')
        except excp.NoSuchElementException:
            pass

        return False

    def scroll_down_for_subscribers(self, number_of_subscribers_to_scroll):
        time.sleep(1)
        element = 'document.querySelectorAll(\'div[role="dialog"]\')[0].children[1]'  # TODO: подумай как обращаться не по классу
        height_of_subscriber_block = 54
        total_scroll = number_of_subscribers_to_scroll * height_of_subscriber_block
        number_of_scrollings = total_scroll // 500 + 1

        self.browser.execute_script('scroll_element = {};'.format(element))
        for i in range(number_of_scrollings):
            time.sleep(1)
            self.browser.execute_script('scroll_element.scrollTop = scroll_element.scrollTop + 500;')

    def subscribe_username(self, username) -> bool:
        """
        Follow user if need and could
        :return: bool
        """
        if self.__could_i_follow():
            self.logger.log('Limit of subscriptions did not reach.')
            # Second if, because we don't need to make http requests if user reaches follow limits
            if self.__do_i_need_to_follow_this_user(username):
                self.logger.log('Have not already followed this user.')
                try:
                    follow_button = self.browser.find_element_by_tag_name('button')
                    follow_button.click()
                    self.db.follows_increment()
                    me.add_subscribed_username(username)
                    self.logger.log('Subscribed on {}.'.format(username))
                    return True
                except excp.NoSuchElementException:
                    self.logger.log('Can\'t find follow button.')
            else:
                self.logger.log('Already follow this user')
        else:
            self.logger.log('Have reached limit of subscriptions.')
        return False

    def unsubscribe_username(self, username) -> bool:
        try:
            subscribe_button = self.browser.find_element_by_tag_name('button')
            subscribe_button.click()
            time.sleep(1)
            subscribe_button = self.browser.find_element(By.CSS_SELECTOR,
                                                         'div[role="dialog"]').find_element_by_tag_name('button')
            subscribe_button.click()
            me.delete_unsubscribed_username(username)
            self.logger.log('Successfully unsubscribed from {}.'.format(username))
            return True
        except excp.NoSuchElementException:
            self.logger.log('Can\'t find unsubscribed button.')
            return False

    def __could_i_follow(self) -> bool:
        """
        Check if i could to follow more
        :return: bool
        """
        counters = self.db.get_follow_limits_by_account()
        return counters['daily'] < 1001 and counters['hourly'] < 76

    def __do_i_need_to_follow_this_user(self, username) -> bool:
        """
        Check if i don't follow this user already
        :return: bool
        """
        self.browser.implicitly_wait(1)

        if self.browser.find_element_by_tag_name('button').text != 'Подписки':
            return True
        return False

    def __get_counters(self, login):
        counters = self.db.get_user_counters(login)
        today = datetime.date.today()
        updated_at = datetime.datetime.strptime(counters['updated_at'], '%Y-%m-%d')
        updated_at_date = datetime.date(year=updated_at.year, month=updated_at.month, day=updated_at.day)
        if (today - updated_at_date).days > 31:
            return {}
        return counters['counters']

    # TODO: refactor this
    def get_like_limits(self, count=None):
        limits = self.db.get_like_limits_by_account()
        today_likes = limits[0]
        hours_left = limits[1]
        hour_likes_by_activity = (self.hour_like_limit * 24 - today_likes) // hours_left
        ll = None
        if self.hour_like_limit <= hour_likes_by_activity < self.hour_like_limit * 2:
            ll = hour_likes_by_activity
        elif hour_likes_by_activity >= self.hour_like_limit * 2:
            ll = self.hour_like_limit * 2
        elif hour_likes_by_activity < self.hour_like_limit:
            ll = hour_likes_by_activity
        self.count = count if 0 < count < ll else ll
        return self.count

    def set_auto_follow(self, flag: bool):
        """
        Enable or disable auto follow mode
        :param flag:
        :return:
        """
        self.auto_follow = flag
        return self

    def get_list_of_subscribers(self, username):  #  Пишет в файл всех подписчиков в файл
        self.logger.log("Getting list {}s\' subscribers.".format(username))
        try:
            ready_subscribers = []
            subscribers_button = self.browser.find_element_by_partial_link_text(
                'подписчиков')  # click on button for getting subscribers
            number_of_subscribers = int(subscribers_button.text.split()[0])
            subscribers_button.click()

            self.scroll_down_for_subscribers(number_of_subscribers_to_scroll=number_of_subscribers)

            list_of_subscribers = self.browser.find_elements(By.CSS_SELECTOR, 'a[title]')
            for i in range(len(list_of_subscribers)):
                try:
                    list_of_subscribers[i] = list_of_subscribers[i].text
                except UnicodeEncodeError:
                    pass

            current_subscribers = me.get_subscribers(format_of_return='list')

            for subscriber in list_of_subscribers:
                if subscriber not in current_subscribers:
                    ready_subscribers.append(subscriber)

            self.logger.log('Got list of subscribers in number of {}.'.format(len(list_of_subscribers)))
            write_subscribers_of_username_to_file(username, list_of_subscribers)
            self.logger.log('Wrote to file {}.json'.format(username))

        except excp.NoSuchElementException:
            self.logger.log('Can\'t find link to followers.')


