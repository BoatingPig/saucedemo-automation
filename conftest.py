import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.edge.options import Options
from pages.login_page import LoginPage
from pages.list_page import ListPage


DEFAULT_USERNAME = "standard_user"
DEFAULT_PASSWORD = "secret_sauce"

@pytest.fixture
def driver():
    # option用来配置浏览器启动时伴随的行为
    options = Options()
    # 打开浏览器时进行最大化
    options.add_argument("--start-maximized")
    driver = webdriver.Edge(options=options)
    yield driver
    driver.quit()


@pytest.fixture
def logged_in_driver(driver):
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(DEFAULT_USERNAME, DEFAULT_PASSWORD)

    list_page = ListPage(driver)

    WebDriverWait(driver, 10).until(expected_conditions.url_contains("inventory.html"))
    list_page.wait_loaded()
    
    return driver
