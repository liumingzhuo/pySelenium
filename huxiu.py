# *_*coding:utf-8 *_*
# 处理滑动验证码
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import re
import requests
from PIL import Image
from io import BytesIO


class huxiu:
    def __init__(self):
        option = self.set_option()
        self.driver = webdriver.Chrome(chrome_options=option)
        self.wait = WebDriverWait(self.driver, 10)

    def set_option(self):
        option = Options()
        option.add_argument('--window-size=1366,768')
        return option

    def go_to_regist(self):
        self.driver.get('https://www.huxiu.com/')
        # 注册按钮
        regist_btn = self.driver.find_element_by_xpath(
            '//div[@class="container"]//a[@class="js-register"]')
        regist_btn.click()
        # 输入手机号
        phone_num = self.wait.until(EC.visibility_of_element_located((
            By.XPATH, '//input[@id="sms_username"]'
        )))
        phone_num.clear()
        phone_num.send_keys('13333333333')

    def get_image(self):
        # 获得有缺口的图片
        img_cut = self.wait.until(EC.presence_of_all_elements_located((
            By.XPATH, '//div[@class="gt_cut_bg gt_show"]/div'
        )))

        img_cut = self.get_complete_img(img_cut)

        # 完整的图片
        img_full = self.wait.until(EC.presence_of_all_elements_located((
            By.XPATH, '//div[@class="gt_cut_fullbg gt_show"]/div'
        )))
        img_full = self.get_complete_img(img_full)
        print(img_cut)
        print(img_full)
        return self.get_img_diff(img_cut, img_full)

    def get_complete_img(self, image):
        url = re.findall(r'url\("(.*?)"\);', image[0].get_attribute('style'))[0]
        print(url)

        img_position_list = [i.get_attribute('style') for i in image]
        img_position_list = [re.findall(r'background-position: -(.*?)px -?(.*?)px;', i)[0] for i in img_position_list]

        img = requests.get(url).content

        img = BytesIO(img)

        img = Image.open(img)

        new_img = Image.new('RGB', (260, 116))

        count_up = 0
        count_down = 0
        for i in img_position_list[:26]:
            img_crop = img.crop((int(i[0]), 58, int(i[0]) + 10, 116))
            new_img.paste(img_crop, (count_up, 0))
            count_up += 10

        for i in img_position_list[26:]:
            img_crop = img.crop((int(i[0]), 0, int(i[0]) + 10, 58))
            new_img.paste(img_crop, (count_down, 58))
            count_down += 10
        return new_img

    def get_img_diff(self, image_crop, image_full):
        def complete_pixel(pixel1, pixel2):
            for i in range(3):
                if abs(pixel1[i] - pixel2[i]) > 50:
                    return False

        for i in range(1, 259):
            for j in range(1, 115):
                crop_pixel = image_crop.getpixel((i, j))
                full_pixel = image_full.getpixel((i, j))
                if complete_pixel(crop_pixel, full_pixel) is False:
                    return i

    def slide_button(self, position):
        slide_btn = self.wait.until(EC.visibility_of_element_located((
            By.XPATH, '//div[@class="gt_slider_knob gt_show"]'
        )))
        ActionChains(self.driver).click_and_hold(slide_btn).perform()
        for i in self.slide_off(position - 2):
            ActionChains(self.driver).move_by_offset(
                xoffset=i, yoffset=0
            ).perform()
        ActionChains(self.driver).release().perform()

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

    def __call__(self, *args, **kwargs):
        self.go_to_regist()
        self.slide_button(self.get_image())


hu = huxiu()
hu()
