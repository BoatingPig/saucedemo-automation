from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException


class BasePage:

    CART_BADGE = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]')
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # 等待-找组件-清空-填文本
    def _type(self, locator, text):
        element = self.wait.until(expected_conditions.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def _click(self, locator):
        element = self.wait.until(expected_conditions.visibility_of_element_located(locator))
        element.click()

    def _text(self, locator):
        element = self.wait.until(expected_conditions.visibility_of_element_located(locator))
        text = element.text
        return text

    def _text_list(self, locator):
        element_list = self.wait.until(expected_conditions.visibility_of_all_elements_located(locator))
        text_list = []
        for element in element_list:
            text_list.append(element.text)
        return text_list

    def _get_all_element(self, locator):
        elements = self.wait.until(expected_conditions.visibility_of_all_elements_located(locator))
        return elements

    def _click_select_value(self, locator, value):
        #等待-获取选择框-弄成对象-点击其中的选项
        element = self.wait.until(expected_conditions.visibility_of_element_located(locator))
        sort_select = Select(element)
        sort_select.select_by_value(value)

    def cart_count(self):
        badges = self.driver.find_elements(*self.CART_BADGE)
        if badges:
            return int(badges[0].text)
        else:
            return 0

    def wait_cart_count(self, expected):
        self.wait.until(
            lambda d: self.cart_count() == expected,
            message=f"购物车角标没有变成 {expected}",
        )

    def cart_count_changed(self, before, timeout=3):
        """短超时轮询：角标是否已经不再是 before。

        变了返回 True，没变返回 False，不抛异常。
        给「这个动作可能根本没生效」的场景用 —— wait_cart_count 会等满 10 秒再抛
        TimeoutException，那种失败信息只说明"超时"，说不出业务原因。
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: self.cart_count() != before
            )
            return True
        except TimeoutException:
            return False

        
