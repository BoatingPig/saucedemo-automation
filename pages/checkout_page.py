from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from pages.base_page import BasePage


def parse_money(text: str) -> float:
    """把 'Item total: $39.98' 解析成 39.98

    结算页的金额都是「说明文字 + $数字」的格式，所以按 $ 切开取后半段。
    """
    return float(text.split("$")[-1].replace(",", "").strip())


class CheckoutInfoPage(BasePage):
    """结算第一步：填写收货信息 checkout-step-one.html"""

    URL = "https://www.saucedemo.com/checkout-step-one.html"

    FIRST_NAME = (By.CSS_SELECTOR, '[data-test="firstName"]')
    LAST_NAME = (By.CSS_SELECTOR, '[data-test="lastName"]')
    POSTAL_CODE = (By.CSS_SELECTOR, '[data-test="postalCode"]')
    CONTINUE_BTN = (By.CSS_SELECTOR, '[data-test="continue"]')
    CANCEL_BTN = (By.CSS_SELECTOR, '[data-test="cancel"]')
    ERROR_MSG = (By.CSS_SELECTOR, '[data-test="error"]')

    def wait_loaded(self):
        self.wait.until(expected_conditions.url_contains("checkout-step-one.html"))
        self.wait.until(expected_conditions.visibility_of_element_located(self.FIRST_NAME))
        return self

    def fill_info(self, first_name, last_name, postal_code):
        # 传空字符串表示"这个字段故意不填"，跳过输入，让表单保持空白
        for locator, value in (
            (self.FIRST_NAME, first_name),
            (self.LAST_NAME, last_name),
            (self.POSTAL_CODE, postal_code),
        ):
            if value:
                self._type(locator, value)

    def submit_info(self, first_name, last_name, postal_code):
        """填写并提交，走成功路径：等到第二步页面加载出来"""
        self.fill_info(first_name, last_name, postal_code)
        self._click(self.CONTINUE_BTN)
        self.wait.until(expected_conditions.url_contains("checkout-step-two.html"))

    def submit_info_expect_error(self, first_name, last_name, postal_code):
        """填写并提交，走校验失败路径：等错误提示出现，返回它的文本"""
        self.fill_info(first_name, last_name, postal_code)
        self._click(self.CONTINUE_BTN)
        # 关键：错误提示是点击之后才被 React 插进 DOM 的，
        # 不等待就去读，拿到的是空字符串或者直接找不到元素
        self.wait.until(expected_conditions.visibility_of_element_located(self.ERROR_MSG))
        return self._text(self.ERROR_MSG)


class CheckoutOverviewPage(BasePage):
    """结算第二步：核对商品与金额 checkout-step-two.html"""

    URL = "https://www.saucedemo.com/checkout-step-two.html"

    PRODUCT_ROW = (By.CSS_SELECTOR, '[data-test="inventory-item"]')
    ROW_NAME = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    ROW_PRICE = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')
    SUBTOTAL = (By.CSS_SELECTOR, '[data-test="subtotal-label"]')
    TAX = (By.CSS_SELECTOR, '[data-test="tax-label"]')
    TOTAL = (By.CSS_SELECTOR, '[data-test="total-label"]')
    FINISH_BTN = (By.CSS_SELECTOR, '[data-test="finish"]')
    CANCEL_BTN = (By.CSS_SELECTOR, '[data-test="cancel"]')

    def wait_loaded(self):
        self.wait.until(expected_conditions.url_contains("checkout-step-two.html"))
        self.wait.until(expected_conditions.visibility_of_element_located(self.SUBTOTAL))
        return self

    def get_row_count(self):
        # 行数可能为 0，不能用 _get_all_element（它会等 10 秒然后抛超时）
        return len(self.driver.find_elements(*self.PRODUCT_ROW))

    def get_row_names(self):
        return [element.text for element in self._get_all_element(self.ROW_NAME)]

    def get_row_prices(self):
        return [parse_money(element.text) for element in self._get_all_element(self.ROW_PRICE)]

    def get_subtotal(self):
        return parse_money(self._text(self.SUBTOTAL))

    def get_tax(self):
        return parse_money(self._text(self.TAX))

    def get_total(self):
        return parse_money(self._text(self.TOTAL))

    def click_finish(self):
        self._click(self.FINISH_BTN)
        self.wait.until(expected_conditions.url_contains("checkout-complete.html"))

    def click_cancel(self):
        self._click(self.CANCEL_BTN)
        self.wait.until(expected_conditions.url_contains("inventory.html"))


class CheckoutCompletePage(BasePage):
    """结算完成页 checkout-complete.html"""

    URL = "https://www.saucedemo.com/checkout-complete.html"

    HEADER = (By.CSS_SELECTOR, '[data-test="complete-header"]')
    TEXT = (By.CSS_SELECTOR, '[data-test="complete-text"]')
    BACK_HOME_BTN = (By.CSS_SELECTOR, '[data-test="back-to-products"]')

    def wait_loaded(self):
        self.wait.until(expected_conditions.url_contains("checkout-complete.html"))
        self.wait.until(expected_conditions.visibility_of_element_located(self.HEADER))
        return self

    def get_header_text(self):
        return self._text(self.HEADER)

    def click_back_home(self):
        self._click(self.BACK_HOME_BTN)
        self.wait.until(expected_conditions.url_contains("inventory.html"))
