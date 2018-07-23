import time

from PIL import Image
from io import BytesIO
from chaojiying import Chaojiying_Client
from auth import USERNAME, PASSWORD

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


class YiDun(object):
    def __init__(self, username, password):
        # 超级鹰账号密码
        self.username = username
        self.password = password
        # 启动chrome
        options = Options()
        options.add_argument('--window-size=1366,768')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.driver, 10)

        # 访问网易易盾

    def start(self):
        self.driver.get('http://dun.163.com/trial/picture-click')
        # 向下滑动，使验证码出现在屏幕中
        self.driver.execute_script("window.scrollTo(0,300)")

    # 获取按钮的位置，把鼠标移动到按钮上，使验证码图片出现
    def go_to_web(self):
        button = self.wait.until(EC.visibility_of_element_located((
            By.XPATH, '//div[@class="tcapt_item is-left"]//div[@class="yidun_tips"]'
        )))
        ActionChains(self.driver).move_to_element(button).perform()

    # 获取验证码图片
    def get_captcha(self):
        # 获取验证码图片的元素
        captcha = self.wait.until(EC.visibility_of_element_located((
            By.XPATH, '//div[@class="tcapt_item is-left"]//img[@class="yidun_bg-img"]'
        )))
        # 获取浏览器整个当前页面的截图
        window_screenshot = self.driver.get_screenshot_as_png()
        # 获取验证码的x,y坐标
        x = captcha.location.get('x')
        y = captcha.location.get('y')
        # 用之前的页面截图生成一个Image对象
        window = Image.open(BytesIO(window_screenshot))
        # 根据验证码图片的坐标，从整个屏幕的图片中截取出验证码。
        crop_image = window.crop((x, y - 300, x + 310, y - 90))
        # 将生成的图片转换成BytesIO，则可以使用getvalue()方法获取图像的二进制数据
        captcha = BytesIO()
        crop_image.save(captcha, format("png"))
        crop_image.show()
        return captcha.getvalue()

    # 使用超级鹰，将图片上传，并获得结果，结果是一个字典，里面有我们的想要的汉字坐标
    def post_captcha_get_position(self, captcha):
        # 传入超级鹰的账号密码，和软件id
        client = Chaojiying_Client(self.username, self.password, '896547')
        # 上传验证码图片，和验证码类型
        data = client.PostPic(captcha, '9103')
        # 字典中的pic_str字段是我们要的汉字坐标，我们用字符串方法分割
        position_list = [i.split(',') for i in data.get('pic_str').split('|')]
        return position_list

    # 点击坐标方法
    def click_position(self, position_list):
        # 找到验证码元素
        captcha = self.wait.until(EC.visibility_of_element_located((
            By.XPATH, '//div[@class="tcapt_item is-left"]//img[@class="yidun_bg-img"]'
        )))
        # 移动鼠标并点击
        last_position = []
        # 遍历坐标列表
        for i in position_list:
            # 点击第一个坐标时直接点击就好
            if not last_position:
                # 将鼠标移动到距离目标元素x,y的位置
                ActionChains(self.driver).move_to_element_with_offset(
                    captcha, int(i[0]), int(i[1])
                ).click().perform()
                # 将当前坐标保存为上一个坐标
                last_position = i
                time.sleep(1)
            # 从第二个坐标开始执行以下部分，匀速移动轨迹
            else:
                # 生产移动轨迹
                track_list = self.track(last_position, i)
                # 按照轨迹逐步移动
                for j in track_list:
                    ActionChains(self.driver).move_to_element_with_offset(
                        captcha, j[0], j[1]
                    ).perform()
                # 点击
                ActionChains(self.driver).click().perform()
                # 将当前坐标保存为上一个坐标
                last_position = i
                time.sleep(1)

    # 生成移动轨迹
    def track(self, last_position, target_position):
        # 将上一个坐标和下一个坐标的X和Y相减，除以20，
        x = (int(target_position[0]) - int(last_position[0])) / 20
        y = (int(target_position[1]) - int(last_position[1])) / 20

        position_list = []
        # 循环20次，生成20个移动位置
        for i in range(1, 21):
            # 根据初始位置生成移动位置
            position = [int(last_position[0]) + round(x * i), int(last_position[1]) + round(y * i)]
            position_list.append(position)

        print(position_list)
        # 返回移动位置
        return position_list

    def __call__(self, *args, **kwargs):
        try:
            self.start()
            # 开始循环，每次检测是否验证成功，成功则跳出循环，不成功则重新执行一次
            while True:
                self.go_to_web()
                captcha = self.get_captcha()
                position_list = self.post_captcha_get_position(captcha)
                self.click_position(position_list)
                # 通过判断按钮元素中是否出现了验证成功的文本，出现了则判断验证成功，失败则继续循环
                try:
                    WebDriverWait(self.driver, 3).until(EC.text_to_be_present_in_element(
                        (By.XPATH, '//div[@class="tcapt_item is-left"]//div[@class="yidun_tips"]'), '验证成功'))
                    break
                except Exception as f:
                    print('验证失败:', f)
                    continue
        except Exception as e:
            print(e)
        finally:
            time.sleep(5)
            self.driver.quit()


if __name__ == '__main__':
    yi = YiDun(USERNAME, PASSWORD)
    yi()
