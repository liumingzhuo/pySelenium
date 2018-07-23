# *_*coding:utf-8 *_*
# 登录猫途鹰

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import requests
from io import BytesIO
from PIL import Image
import time
from auth import USERNAME, PASSWORD
import json


class trip_advisor:
    def __init__(self):
        option = self.set_option()
        self.driver = webdriver.Chrome(chrome_options=option)
        self.wait = WebDriverWait(self.driver, 10)

    def set_option(self):
        option = Options()
        option.add_argument('--window-size=1366,768')
        return option

    # 进入主页 并点出注册或登录
    def go_trip(self):
        try:
            self.driver.get('https://www.tripadvisor.cn/')
            regist_btn = self.driver.find_element_by_xpath(
                '//a[@class="ui_button secondary small login-button core-login-button"]')
            regist_btn.click()
            self.driver.switch_to.frame(self.driver.find_element_by_xpath('//iframe[@id="overlayRegFrame"]'))
            time.sleep(1)
        except Exception as e:
            print('进入登录页错误', e)
            self.driver.quit()

    def input_acc_psw(self):
        account = self.driver.find_element_by_xpath('//input[@class="text focusClear regInputText"]')
        account.clear()
        account.send_keys(USERNAME)
        psw = self.driver.find_element_by_xpath('//div[@class="centerCol"]//input[@class="text regInputText"]')
        psw.clear()
        psw.send_keys(PASSWORD)

    def get_image(self):
        # 切换到子框架
        try:
            img_crop = self.wait.until(EC.presence_of_all_elements_located((
                By.XPATH, '//div[@class="gt_cut_bg gt_show"]/div'
            )))
            img_crop = self.get_complete_img(img_crop)
            img_full = self.wait.until(EC.presence_of_all_elements_located((
                By.XPATH, '//div[@class="gt_cut_fullbg gt_show"]/div'
            )))
            img_full = self.get_complete_img(img_full)
            return self.get_img_diff(img_crop, img_full)
        except Exception as e:
            print('获取图片出现错误', e)
            self.driver.quit()

    # 拼成完整的图片
    def get_complete_img(self, image):
        try:
            img_url = re.findall(r'url\("(.*?)"\);', image[0].get_attribute('style'))[0]

            img_position_list = [i.get_attribute('style') for i in image]

            img_position_list = [re.findall(r'background-position: -(.*?)px -?(.*?)px;', i)[0] for i in
                                 img_position_list]

            img = requests.get(img_url).content

            img = BytesIO(img)

            img = Image.open(img)

            img_new = Image.new('RGB', (260, 116))

            count_up = 0
            count_down = 0

            for i in img_position_list[:26]:
                img_crop = img.crop((int(i[0]), 58, int(i[0]) + 10, 116))
                img_new.paste(img_crop, (count_up, 0))
                count_up += 10

            for i in img_position_list[26:]:
                img_crop = img.crop((int(i[0]), 0, int(i[0]) + 10, 58))
                img_new.paste(img_crop, (count_down, 58))
                count_down += 10
            return img_new
        except Exception as e:
            print('拼接图片出现错误', e)
            self.driver.quit()

    # 找出缺口位置 并计算出距离
    def get_img_diff(self, image_crop, image_full):
        def complete_pixel(pixel1, pixel2):
            for i in range(3):
                if abs(pixel1[i] - pixel2[i]) > 50:
                    return False

        for i in range(1, 259):
            for j in range(1, 115):
                img_crop = image_crop.getpixel((i, j))
                img_full = image_full.getpixel((i, j))
                if complete_pixel(img_crop, img_full) is False:
                    return i

    def slide_button(self, position):
        try:
            slide_btn = self.wait.until(EC.visibility_of_element_located((
                By.XPATH, '//div[@class="gt_slider_knob gt_show"]'
            )))
            ActionChains(self.driver).click_and_hold(slide_btn).perform()
            for i in self.slide_off(position - 2):
                ActionChains(self.driver).move_by_offset(xoffset=i, yoffset=0).perform()
            ActionChains(self.driver).release().perform()
        except Exception as e:
            print('滑动发生异常', e)
            self.driver.quit()

    # 移动距离
    def slide_off(self, position):
        t = 0.2
        current = 0
        change_speed = position / 3 * 5
        speed = 0
        move_distance_list = []
        while current < position:
            if current < change_speed:
                a = 3
                distance = speed * t + 0.5 * a * t * t
                move_distance_list.append(round(distance))
                speed += (a * t)
                current += distance
            else:
                move_distance_list.extend([3, 3, 2, 2, 1, 1])
                break
        offset = sum(move_distance_list) - position
        if offset < 0:
            move_distance_list.extend([1 for i in range(abs(offset))])
        elif offset > 0:
            move_distance_list.extend([-1 for i in range(abs(offset))])

        move_distance_list.extend(
            [0, 0, 0, 0, -1, -1, -1, 0, 0, 0, -1, -1, -1, 1, 1]
        )
        return move_distance_list

    def go_to_log(self):
        login_btn = self.wait.until(EC.visibility_of_element_located((
            By.XPATH,
            '//div[@class="centerCol"]//div[@class="ui_button primary regSubmitBtn"]'
        )))
        ActionChains(self.driver).click(login_btn).perform()
        self.save_cookies()

    # 保存cookies
    def save_cookies(self):
        time.sleep(3)
        cookies = self.driver.get_cookies()
        with open('cookies.txt', 'w') as f:
            json.dump(cookies, f)

    def __call__(self, *args, **kwargs):
        self.go_trip()
        self.input_acc_psw()
        self.slide_button(self.get_image())
        self.go_to_log()


trip = trip_advisor()
trip()
