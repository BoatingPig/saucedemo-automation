from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions
from pages.base_page import BasePage

class LoginPage(BasePage):
    #定义登录界面的url
    URL = "https://www.saucedemo.com/"

    USERNAME = (By.CSS_SELECTOR, '[data-test="username"]')
    PASSWORD = (By.CSS_SELECTOR, '[data-test="password"]')
    LOGIN_BTN = (By.CSS_SELECTOR, '[data-test="login-button"]')
    ERROR = (By.CSS_SELECTOR, '[data-test="error"]')

    # 初始化
    # def __init__(self, driver):
    #     self.driver = driver
    #     self.wait = WebDriverWait(driver, 10)

    # 请求类中规定的登录界面URL
    def open(self):
        self.driver.get(self.URL)

    # 传入账号和密码，并点击登录按钮
    def login(self, username, password):
        self._type(self.USERNAME, username)
        self._type(self.PASSWORD, password)
        self._click(self.LOGIN_BTN)

    def error_msg(self):
        return self._text(self.ERROR)
