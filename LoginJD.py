from selenium import webdriver
from PIL import Image
import time
import re

from selenium.webdriver import ActionChains


class LoginJD(object):
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()
        self.driver.get("https://passport.jd.com/new/login.aspx")
        self.driver.find_element_by_link_text("账户登录").click()
        self.driver.find_element_by_id("loginname").send_keys("loginname")
        self.driver.find_element_by_id("nloginpwd").send_keys("nloginpwd")
        self.driver.find_element_by_id("loginsubmit").click()
        time.sleep(3)
        self.img = self.driver.find_element_by_css_selector(
            "div.JDJRV-bigimg>img")  # 定位滑块背景的图片
        style = self.driver.find_element_by_css_selector(
            "div.JDJRV-smallimg").get_attribute("style")  # 获取滑块的style值
        top = re.findall(r"(\d+)", style)[0]  # 通过正则获取滑块的top值
        self.y = int(top) + 9  # 滑块的top值+9就是缺口的最上边的边框的纵坐标

    def save_image(self):
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
        self.save_image()
        im = Image.open('verifyCode.png')  # 保存灰度化处理后的图片
        width = im.size[0]
        im = im.convert('RGB')
        x_list = []
        print(self.y)
        for x in range(width):
            r, g, b = im.getpixel((x, self.y))   # 获取灰度化之后的缺口最上方的纵坐标所有的RGB值
            if r + g + b < 240:   # 获取RGB值和小于220的横坐标
                x_list.append(x)
        print(x_list)
        for x in x_list:
            m = 0
            for i in range(33):
                if x + i in x_list:
                    m += 1
                if m == 22:
                    print(x)
                    return x

    def get_track(self):
        distance = self.get_width_value()
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 1
        while current < distance:
            if current < mid:
                # 加速度为2
                a = 4
            else:
                # 加速度为-2
                a = -3
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move(self):
        tracks = self.get_track()
        move_icon = self.driver.find_element_by_css_selector(
            "div.JDJRV-slide-inner.JDJRV-slide-btn")
        ActionChains(self.driver).click_and_hold(move_icon).perform()
        for x in tracks:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()
        time.sleep(10)
        self.driver.quit()


if __name__ == '__main__':
    j = LoginJD()
    j.move()
