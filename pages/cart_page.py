from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

class CartPage(BasePage):

    URL = "https://www.saucedemo.com/cart.html"

    PRODUCT_ROW = (By.CSS_SELECTOR, '[data-test="inventory-item"]')
    ROW_NAME = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    ROW_PRICE = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')
    CONTINUE_SHOPPING_BTN = (By.CSS_SELECTOR, '[data-test="continue-shopping"]')
    CHECKOUT_BTN = (By.CSS_SELECTOR, '[data-test="checkout"]')

    def get_all_rows(self):
        return self._get_all_element(self.PRODUCT_ROW)

    def get_title_and_price_from_rows(self,rows):
        products_list = []
        for row in rows:
            title = row.find_element(*self.ROW_NAME).text
            price = row.find_element(*self.ROW_PRICE).text
            products_list.append((title, price))
        return products_list

    def remove_product(self, title):
        locator = (By.CSS_SELECTOR, f'[data-test="remove-{title.lower().replace(" ", "-")}"]')
        expected_count = self.cart_count() - 1
        self._click(locator)
        self.wait_cart_count(expected_count)

    def click_continue_shopping(self):
        self._click(self.CONTINUE_SHOPPING_BTN)
        self.wait.until(expected_conditions.url_contains("inventory.html"))

    def click_checkout(self):
        before_url = self.driver.current_url
        self._click(self.CHECKOUT_BTN)
        try:
            self.wait.until(expected_conditions.url_contains("checkout-step-one.html"))
        except TimeoutError :
            after_url = self.driver.current_url
            print("yhy checkout timeout")
            print(f"befor_url = {before_url}")
            print(f"after_url = {after_url}")


    def get_row_count(self):
        return len(self.driver.find_elements(*self.PRODUCT_ROW))



