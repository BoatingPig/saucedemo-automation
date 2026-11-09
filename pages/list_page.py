from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from data.expected_products import EXPECTED_PRODUCTS

class ListPage(BasePage):

    URL = "www.saucedemo.com/inventory.html"

    PRODUCT_TITLE = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')

    PRODUCT_PRICE = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')

    PRODUCT_IMG = (By.TAG_NAME, "img")

    CARD = (By.CSS_SELECTOR, '[data-test="inventory-item"]')

    CART_BUTTON = (By.CSS_SELECTOR, '[data-test="shopping-cart-link"]')

    CART_BADGE = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]')

    SORT_SELECT = (By.CSS_SELECTOR, '[data-test="product-sort-container"]')

    ADD_BTN_TEXT = "Add to cart"

    REMOVE_BTN_TEXT = "Remove"

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
        elements_item = self._get_all_element(self.CARD)
        #用一个列表，里装元组，把标题和价格放一起
        list = []
        #拿到商品卡片item，里面包括价格和标题的元素
        #想让这个卡片item作为父元素，在其中找标题和价格，这样就可以认为他们是同一个商品下的
        #已经拿到了卡片元素，里面的子元素应该就不用wait了
        for item in elements_item:
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

    def click_sort_select_value(self, value):
        titles_before = self.get_all_products_title()
        self._click_select_value(self.SORT_SELECT, value)
        self.wait.until(
        lambda d: self.get_all_products_title() != titles_before,
        message=f"选择排序 {value} 后商品列表顺序没有变化",
    )

    def check_sort_products(self, products_list, target="title", order="asc"):
        #判断排序方式
        
        products_title_price_list = [(item[0], item[1]) for item in products_list]
        expected_products = dict(EXPECTED_PRODUCTS)

        #现在商品名对应价格和期望表里的同一个商品名拿到的价格是一致的
        
        if not all(item[1] == expected_products[item[0]] for item in products_title_price_list):
            raise AssertionError("product's price is not expected")
        
        if target == "title":
            target_list = [(item[0]) for item in products_list]
        elif target == "price":
            #需要拆成浮点数的再比较
            target_list = [float((item[1]).replace("$","")) for item in products_list]
        else:
             raise AssertionError("sort order,target parameter error")

        #升序
        if order == "asc":
            #确保商品名排序是升序
            return all(title1 <= title2 for title1,title2 in zip(target_list, target_list[1:]))
        elif order == "desc":
            #确保商品名排序是降序
            return all(title1 >= title2 for title1,title2 in zip(target_list, target_list[1:]))
        else:
            raise AssertionError("sort order,order parameter error")


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

    def add_to_cart(self, title):
        # 找到商品对应的card，然后点他的button
        # 根据title去拼接名字
        expected = self.cart_count() + 1
        add_locator = (By.CSS_SELECTOR, f'[data-test="add-to-cart-{title.lower().replace(" ", "-")}"]')
        self._click(add_locator)
        self.wait_cart_count(expected)

    def remove_from_cart(self, title):
        expected = self.cart_count() - 1
        remove_locator = (By.CSS_SELECTOR, f'[data-test="remove-{title.lower().replace(" ", "-")}"]')
        self._click(remove_locator)
        self.wait_cart_count(expected)

    def button_text(self, title, order="add"):
        if order == "add":
            locator = (By.CSS_SELECTOR, f'[data-test="add-to-cart-{title.lower().replace(" ", "-")}"]')
        elif order == "remove":
            locator = (By.CSS_SELECTOR, f'[data-test="remove-{title.lower().replace(" ", "-")}"]')
        else:
            return None
        btn_text = self._text(locator)

        return btn_text

    #获取列表页面中已在购物车的商品
    def get_card_product_from_page(self):
        products_list = self.get_all_products_title_and_price_and_img()
        products_in_cart_list = []
        for item in products_list:
            locator = (By.CSS_SELECTOR, f'[data-test="remove-{item[0].lower().replace(" ", "-")}"]')
            if self.driver.find_elements(*locator):
                products_in_cart_list.append((item[0], item[1]))

        return products_in_cart_list

    

        



        