# -*- coding: utf-8 -*-
import os

try:
    script_path = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(script_path + '/var'):
        os.mkdir(script_path + '/var')
    var_path = os.path.join(script_path, 'var')
    if not os.path.exists(var_path + '/cookie'):
        os.mkdir(var_path + '/cookie')
    COOKIE_PATH = os.path.join(var_path, 'cookie')
    if not os.path.exists(var_path + '/log'):
        os.mkdir(var_path + '/log')
    LOG_PATH = os.path.join(var_path, 'log')
    DB_PATH = os.path.join(var_path, 'db')

    exclude = open(os.path.join(var_path, 'exclude_accounts.txt')).read().split(',')
except FileNotFoundError:
    print('Something wrong with configurations files. Try to restore init configuration.')
