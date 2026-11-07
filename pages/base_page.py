from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class BasePage:
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
