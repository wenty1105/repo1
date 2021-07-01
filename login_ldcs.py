# coding=utf-8
from PIL import Image
from selenium import webdriver
import time
import re
import numpy as np
from selenium.webdriver import ActionChains


class LoginByLDCSCanvas(object):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()  # 最大化页面
        self.driver.implicitly_wait(5)  # 隐式等待5秒
        self.driver.get(
            'https://ldcssit.cnsuning.com/ldcs-web/main/login.htm')  # 登录LDCS页面
        self.driver.find_element_by_id(
            "userCode").send_keys("18011504")  # 输入账号
        self.driver.find_element_by_id("pwd").send_keys('Sn112233')  # 输入密码
        time.sleep(2)
        self.driver.find_element_by_id(
            "captcha_sncaptcha_button").click()  # 点击图片验证
        self.img = self.driver.find_element_by_css_selector(
            "div.tobe-obfuscate-image-wrap-box")  # 定位滑块背景的图片
        style = self.driver.find_element_by_css_selector(
            "img.tobe-obfuscate-image-fragment").get_attribute("style")  # 获取滑块的style值
        top = re.findall(r"(\d+)", style)[0]  # 通过正则获取滑块的top值
        self.y = int(top) + 12  # 滑块的top值+12就是缺口的最上边的边框的纵坐标

    def get_image(self):
        time.sleep(1)
        img_location = self.img.location  # 获取滑动背景的位置
        img_size = self.img.size  # 获取滑动背景的大小
        left = img_location['x']  # 获取滑动背景横坐标
        top = img_location['y']  # 获取滑动背景纵坐标
        right = left + img_size['width']  # 获取滑动背景图片的宽+横坐标
        bottom = top + img_size['height']  # 获取滑动背景图片的长+纵坐标
        self.driver.save_screenshot('1.png')  # 保存当前页面为图片
        img_full_screen = Image.open('1.png')
        img_verify_code = img_full_screen.crop(
            (left, top, right, bottom))  # 截取滑动的背景图片
        img_verify_code.save('verifyCode.png')  # 保存滑动的背景图片

    def get_width_value(self):
        self.get_image()
        a = np.array(Image.open("verifyCode.png").convert('L'))  # 图片灰度化
        b = 255 - a
        imb = Image.fromarray(b.astype("uint8"))  # 灰度化处理
        imb.save("imb.png")
        im = Image.open('imb.png')  # 保存灰度化处理后的图片
        width = im.size[0]
        im = im.convert('RGB')
        x_list = []
        for x in range(width - 40):
            r, g, b = im.getpixel((x, self.y))   # 获取灰度化之后的缺口最上方的纵坐标所有的RGB值
            if r > 190 and g > 190 and b > 190:   # 获取RGB值都大于190的横坐标
                x_list.append(x)
        for x in x_list:  # 分析列表x_list
            # 找到x_list中的第一个数字后连续40数有24个在x_list中的值
            m = 0
            for x_len in range(40):
                if x + x_len in x_list:
                    m += 1
                if m >= 24:
                    return x

    def move(self):
        move_icon = self.driver.find_element_by_css_selector(
            "div.tobe-obfuscate-slider.transparent-icon")
        x_offset = self.get_width_value()
        ActionChains(
            self.driver).drag_and_drop_by_offset(
            move_icon, x_offset - 6, 0).perform()
        time.sleep(10)

    def drive_quite(self):
        self.driver.quit()


if __name__ == '__main__':
    p = LoginByLDCSCanvas()
    p.move()
    p.drive_quite()
