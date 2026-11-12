import pytest
import os
from pytest_html import extras
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时截图，直接嵌进 HTML 报告。

    为什么不写在 driver fixture 的 yield 之后：
    1. makereport 在「阶段结束时」触发，此时 driver 还活着（teardown 还没跑）
    2. setup 阶段就挂的用例（比如前置 fixture 建不起来）走不到 yield 之后
    3. 写在这里能同时覆盖 setup 失败和 call 失败，且不影响任何用例逻辑
    """
    outcome = yield
    report = outcome.get_result()

    # teardown 阶段 driver 已经 quit，截不了；只处理 setup / call
    if report.when not in ("setup", "call") or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    try:
        png = driver.get_screenshot_as_base64()
    except Exception:
        # 截图本身失败不能把报告搞挂，静默跳过
        return

    if not hasattr(report, "extras"):
        report.extras = []
    report.extras.append(extras.image(png, mime_type="image/png"))


@pytest.fixture
def driver():
    # option用来配置浏览器启动时伴随的行为
    
    is_ci = os.getenv('CI') == "true"
    headless = os.getenv("HEADLESS") == "1"

    if is_ci:
        options = webdriver.ChromeOptions()
    else:
        options = webdriver.EdgeOptions()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-gpu")
    if is_ci:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-gpu")
    
    options.add_argument("--window-size=1920,1080")
    # 打开浏览器时进行最大化

    if is_ci:
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Edge(options=options)
    yield driver
    driver.quit()


@pytest.fixture
def logged_in_driver(request, driver):
    """登录后的 driver，默认用 standard_user。

    换账号的两种方式（都不会影响已有的 44 条用例）：
      1. 环境变量：SAUCE_USER=problem_user pytest ...
      2. 参数化 fixture（推荐，因为对照组写在同一个文件里，看得见）：
         @pytest.mark.parametrize("logged_in_driver", ["problem_user"], indirect=True)

    这里不能挂 params=，否则整个项目会乘以账号数：
    logged_in_driver 是所有 fixture 的根，它 ×5 等于所有用例 ×5。
    """
    login_page = LoginPage(driver)
    login_page.open()

    username = getattr(request, "param", os.getenv("SAUCE_USER", DEFAULT_USERNAME))
    login_page.login(username, DEFAULT_PASSWORD)

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
    list_page = ListPage(cart_with_n_items)
    list_page.go_to_cart()

    CartPage(cart_with_n_items).click_checkout()
    CheckoutInfoPage(cart_with_n_items).wait_loaded()
    return cart_with_n_items


@pytest.fixture
def checkout_overview_driver(checkout_info_driver):
    CheckoutInfoPage(checkout_info_driver).submit_info(**DEFAULT_CHECKOUT_INFO)

    CheckoutOverviewPage(checkout_info_driver).wait_loaded()
    return checkout_info_driver
    
    
