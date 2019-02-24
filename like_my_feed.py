# -*- coding: utf-8 -*-
if __name__ == "__main__":
    import argparse

    import configure
    from User import me
    from insta_browser import browser

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='enable debug mode', action="store_true")
    parser.add_argument('--count', help='if indicated, like posts by count', type=int, default=0)
    args = parser.parse_args()
    debug = args.debug
    count = args.count

    login = me.get_login()
    password = me.get_password()
    try:
        br = browser.Browser(
            debug=debug,
            cookie_path=configure.COOKIE_PATH,
            log_path=configure.LOG_PATH,
            exclude=configure.exclude,
            db_path=configure.DB_PATH,
        )

        try:
            br.auth(login, password)
            br.process_feed(count)
            print(br.get_summary())
        finally:
            br.close_all()

    except Exception as e:
        print(e)
        input()