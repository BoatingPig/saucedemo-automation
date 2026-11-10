import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.edge.options import Options
from pages.login_page import LoginPage
from pages.list_page import ListPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutInfoPage, CheckoutOverviewPage
from data.expected_products import EXPECTED_PRODUCTS


DEFAULT_USERNAME = "standard_user"
DEFAULT_PASSWORD = "secret_sauce"
DEFAULT_PRODUCT_TITLE = "Sauce Labs Backpack"

# 结算第一步的一组合法收货信息，多处复用
DEFAULT_CHECKOUT_INFO = {
    "first_name": "San",
    "last_name": "Zhang",
    "postal_code": "100000",
}

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

@pytest.fixture
def cart_had_product_driver(logged_in_driver):
    list_page = ListPage(logged_in_driver)
    
    before_cart_count = list_page.cart_count()
        
    list_page.add_to_cart(DEFAULT_PRODUCT_TITLE)
    
    after_cart_count = list_page.cart_count()
    
        # 点击之后，断言
    assert after_cart_count - before_cart_count == 1
    assert list_page.button_text(DEFAULT_PRODUCT_TITLE, "remove") == ListPage.REMOVE_BTN_TEXT
    return logged_in_driver


@pytest.fixture
def cart_with_n_items(request, logged_in_driver):
    """前置：购物车里有 N 件商品。

    默认 1 件；想换数量就参数化 fixture 本身（indirect=True）：
        @pytest.mark.parametrize("cart_with_n_items", [1, 3, 6], indirect=True)
    用 request.param 取参数，所以不会像普通参数化那样给每条用例传一个列表。
    """
    count = getattr(request, "param", 1)

    list_page = ListPage(logged_in_driver)
    for title in [item[0] for item in EXPECTED_PRODUCTS][:count]:
        list_page.add_to_cart(title)

    # 前置条件没搭成就该报 ERROR，而不是让用例带着错误状态继续跑
    assert list_page.cart_count() == count
    return logged_in_driver


@pytest.fixture
def checkout_info_driver(cart_with_n_items):
    """前置：购物车有商品，并且已经停在结算第一步"""
    list_page = ListPage(cart_with_n_items)
    list_page.go_to_cart()

    CartPage(cart_with_n_items).click_checkout()
    CheckoutInfoPage(cart_with_n_items).wait_loaded()
    return cart_with_n_items


@pytest.fixture
def checkout_overview_driver(checkout_info_driver):
    """前置：收货信息已填好，并且已经停在结算第二步"""
    CheckoutInfoPage(checkout_info_driver).submit_info(**DEFAULT_CHECKOUT_INFO)

    CheckoutOverviewPage(checkout_info_driver).wait_loaded()
    return checkout_info_driver
    
    
