# *_*coding:utf-8 *_*
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import requests
from PIL import Image
import time


class yiDun:
    def __init__(self):
        self.option = self.set_options()
        self.driver = webdriver.Safari()
        self.wait = WebDriverWait(self.driver, 10)

    def set_options(self):
        option = Options()
        option.add_argument('--window-size=1366,768')
        return option

    # 访问  并找到验证码图片
    def get_image(self):
        self.driver.get('http://dun.163.com/trial/picture-click')
        self.driver.execute_script('window.scrollTo(0,300)')
        button = self.wait.until(EC.visibility_of_element_located((
            By.XPATH, '//div[@class="tcapt_item is-left"]//div[@class="yidun_tips"]'
        )))
        ActionChains(self.driver).move_to_element(button).perform()
        # 截屏
        caption = self.wait.until(EC.visibility_of_element_located((
            By.XPATH, '//div[@class="tcapt_item is-left"]//img[@class="yidun_bg-img"]'
        )))
        self.driver.save_screenshot('yidun.png')
        x, y = caption.location.values()
        print(x, y)
        window = Image.open('yidun.png')
        caption = window.crop((x, y - 300, x + 310, y - 90))
        caption.show()

    def __call__(self, *args, **kwargs):
        try:
            self.get_image()
        except Exception as e:
            print(e)
            time.sleep(5)
            self.driver.quit()


yidun = yiDun()
yidun()
