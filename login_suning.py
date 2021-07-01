from selenium import webdriver
from PIL import Image
import time
import re
from selenium.webdriver import ActionChains


class LoginSuning(object):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        self.driver.get("https://passport.suning.com/ids/login")
        time.sleep(2)
        self.driver.find_element_by_xpath("//span[text()='账户登录']").click()  # 点击账户登录
        self.driver.find_element_by_id("userName").send_keys("test")  # 输入账号
        self.driver.find_element_by_id("password").send_keys("test")  # 输入密码
        time.sleep(3)
        self.driver.find_element_by_id("iar1_sncaptcha_button").click()  # 点击按钮进行验证
        time.sleep(10)
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
        im = Image.open('verifyCode.png')  # 保存灰度化处理后的图片
        width = im.size[0]
        im = im.convert('RGB')
        x_list = []
        print(self.y)
        for x in range(width):
            r, g, b = im.getpixel((x, self.y))   # 获取灰度化之后的缺口最上方的纵坐标所有的RGB值
            if r + g + b < 180:   # 获取RGB值和小于180的横坐标
                x_list.append(x)
        print(x_list)
        for x in x_list:
            m = 0
            for i in range(40):
                if x + i in x_list:
                    m += 1
                if m == 24:
                    print(x)
                    return x

    def move(self):
        move_icon = self.driver.find_element_by_css_selector(
                    "div.tobe-obfuscate-slider.transparent-icon")
        x_offset = self.get_width_value()
        ActionChains(
            self.driver).drag_and_drop_by_offset(
            move_icon, x_offset - 6, 0).perform()
        time.sleep(10)
        self.driver.quit()


if __name__ == '__main__':
    login = LoginSuning()
    login.move()
