from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class ListPage(BasePage):

    URL = "www.saucedemo.com/inventory.html"

    PRODUCT_TITLE = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')

    PRODUCT_PRICE = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')

    PRODUCT_ITEM = (By.CSS_SELECTOR, '[data-test="inventory-item"]')

    PRODUCT_IMG = (By.TAG_NAME, "img")

    CARD = (By.CSS_SELECTOR, '[data-test="inventory-item"]')

    CART_BUTTON = (By.CSS_SELECTOR, '[data-test="shopping-cart-link"]')

    # def __init__(self, driver):
    #     self.driver = driver
    #     self.wait = WebDriverWait(driver, 10)

    def wait_loaded(self):
        self.wait.until(expected_conditions.presence_of_all_elements_located(self.CARD))
        return self

    def get_all_products_title(self):
        list = self._text_list(self.PRODUCT_TITLE)
        return list

    def get_all_products_title_and_price_and_img(self):
        elemensts_item = self._get_all_element(self.PRODUCT_ITEM)
        #用一个列表，里装元组，把标题和价格放一起
        list = []
        #拿到商品卡片item，里面包括价格和标题的元素
        #想让这个卡片item作为父元素，在其中找标题和价格，这样就可以认为他们是同一个商品下的
        #已经拿到了卡片元素，里面的子元素应该就不用wait了
        for item in elemensts_item:
            # print(elemensts_item[0].get_attribute("outerHTML"))
            price_element = item.find_element(*self.PRODUCT_PRICE)
            raw_price = price_element.text
            price = raw_price.replace("\n", "")
            # match = re.search(r'\d+(\.\d+)?', raw_price)
            # if match:
            #     price = match.group()

            title_element = item.find_element(*self.PRODUCT_TITLE)
            title = title_element.text

            img_element = item.find_element(*self.PRODUCT_IMG)

            list.append((title, price, img_element))

        return list
        

    def get_product_cards_count(self):
        count = len(self._get_all_element(self.CARD))
        return count

    def go_to_cart(self):
        self._click(self.CART_BUTTON)
        self.wait.until(expected_conditions.url_contains("cart.html"))

    def wait_img_loaded(self, imges):
        #需要等到页面的图片加载
        #首先要拿到img的元素信息
        #要driver去页面那img里一个属性的参数
        WebDriverWait(self.driver, 10).until(
            #匿名函数
            lambda d:
            #拿每一个img元素，让driver去js请求img中的complete属性
            #arguments[0]相当于一个占位符，转成js后img会放到其中 => img.complete
              all(d.execute_script("return arguments[0].complete", img) for img in imges)
        )
        

    

        



        