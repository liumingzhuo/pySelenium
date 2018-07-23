# *_*coding:utf-8 *_*
# 使用cookies登录猫途鹰
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import requests


class login_trip:
    def __init__(self):
        self.url = 'https://www.tripadvisor.cn/'
        # self.use_chrome(self.open_cookies())
        self.use_request(self.open_cookies())

    def use_chrome(self, cookis):
        options = Options()
        options.add_argument('--window-size=1366,768')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(self.url)
        time.sleep(3)
        for cook in cookis:
            self.driver.add_cookie(cook)
        self.driver.get(self.url)

    def use_request(self, cooki):
        session = requests.Session()
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        }
        coo = {}
        for cook in cooki:
            coo[cook['name']] = cook['value']
        # 方法1 使用cookies
        # result = session.get(self.url, cookies=coo)

        # 方法2 使用cookiejar
        # cookiejar = requests.utils.cookiejar_from_dict(coo)
        # session.cookies = cookiejar
        # result = session.get(self.url)
        # print(result.status_code)

        # 方法3 将字典转换成cookiejar
        requests.utils.add_dict_to_cookiejar(session.cookies, coo)
        result = session.get(self.url)
        self.save_cookies_dic(session)

    def open_cookies(self):
        with open('cookies.txt', 'r') as f:
            return json.load(f)

    # 将cookies转成字典
    def save_cookies_dic(self, session):
        cookie_dic = requests.utils.dict_from_cookiejar(session.cookies)
        with open('cookie_dic.txt', 'a') as f:
            json.dump(cookie_dic, f)

        pass


login = login_trip()
