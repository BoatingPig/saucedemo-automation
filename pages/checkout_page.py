from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from pages.base_page import BasePage


def parse_money(text: str) -> float:
    return float(text.split("$")[-1].replace(",", "").strip())


class CheckoutInfoPage(BasePage):
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
        self.fill_info(first_name, last_name, postal_code)
        self._click(self.CONTINUE_BTN)
        self.wait.until(expected_conditions.url_contains("checkout-step-two.html"))

    def submit_info_expect_error(self, first_name, last_name, postal_code):
        self.fill_info(first_name, last_name, postal_code)
        self._click(self.CONTINUE_BTN)
        error_element = self.wait.until(expected_conditions.visibility_of_element_located(self.ERROR_MSG))
        return error_element.text


class CheckoutOverviewPage(BasePage):

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
        return len(self.driver.find_elements(*self.PRODUCT_ROW))
       

    def get_row_titles(self):
        return [element.text for element in self._get_all_element(self.ROW_NAME)]

    def get_row_prices(self):

        row_price = self._get_all_element(self.ROW_PRICE)
        total_price = []
        for row in row_price:
            total_price.append(parse_money(row.text))
        return total_price

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