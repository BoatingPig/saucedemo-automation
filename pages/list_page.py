from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from data.expected_products import EXPECTED_PRODUCTS

class ListPage(BasePage):

    URL = "www.saucedemo.com/inventory.html"

    PRODUCT_TITLE = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')

    PRODUCT_PRICE = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')

    PRODUCT_IMG = (By.TAG_NAME, "img")

    CARD = (By.CSS_SELECTOR, '[data-test="inventory-item"]')

    CART_BUTTON = (By.CSS_SELECTOR, '[data-test="shopping-cart-link"]')

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
        # 前端路由会先把 URL 改掉、再渲染新页面，所以 URL 对了不等于 DOM 换完了。
        # 不等这个元素，紧接着读购物车行数有可能读到列表页的 6 张卡片。
        self.wait.until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '[data-test="cart-list"]'))
        )

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

    def select_sort_value(self, value):
        """只选择排序项，不等列表刷新。

        给「预期排序可能不生效」的用例用：正常用例应该用 click_sort_select_value，
        那里有等待；但如果列表本来就该保持原样，等待一个永远不会发生的变化
        只会白等满 10 秒，再抛一个和真实原因无关的 TimeoutException。
        """
        self._click_select_value(self.SORT_SELECT, value)

    def click_sort_select_value(self, value):
        titles_before = self.get_all_products_title()
        self.select_sort_value(value)
        self.wait.until(
        lambda d: self.get_all_products_title() != titles_before,
        message=f"选择排序 {value} 后商品列表顺序没有变化",
    )

    def sort_order_changed(self, titles_before, timeout=3):
        """短超时轮询：列表顺序是否已经变了。变了返回 True，没变返回 False。

        和 click_sort_select_value 的区别：那个会等满 10 秒再抛异常，适合
        「排序一定生效」的正常用例；这个快速返回布尔值，适合「排序可能不生效」的场景。
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: self.get_all_products_title() != titles_before
            )
            return True
        except TimeoutException:
            return False

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

    def add_to_cart(self, title):
        # 找到商品对应的card，然后点他的button
        # 根据title去拼接名字
        before = self.cart_count()
        add_locator = (By.CSS_SELECTOR, f'[data-test="add-to-cart-{title.lower().replace(" ", "-")}"]')
        self._click(add_locator)
        if not self.cart_count_changed(before, timeout=5):
            raise AssertionError(f"点了 Add to cart，角标还是 {before}，这次点击没生效：{title}")

    def remove_from_cart(self, title):
        before = self.cart_count()
        remove_locator = (By.CSS_SELECTOR, f'[data-test="remove-{title.lower().replace(" ", "-")}"]')
        self._click(remove_locator)
        if not self.cart_count_changed(before, timeout=5):
            raise AssertionError(f"点了 Remove，角标还是 {before}，这次点击没生效：{title}")

    def _card_button_locator(self, title, order="add"):
        """卡片上那个按钮的定位器：加购按钮和移除按钮的 data-test 只差前缀。"""
        slug = title.lower().replace(" ", "-")
        if order == "add":
            return (By.CSS_SELECTOR, f'[data-test="add-to-cart-{slug}"]')
        elif order == "remove":
            return (By.CSS_SELECTOR, f'[data-test="remove-{slug}"]')
        raise ValueError(f'order 只能是 "add" 或 "remove"，收到 {order!r}')

    def click_card_button(self, title, order="add"):
        """只点卡片上的按钮，不等角标变化。

        给「这个按钮可能根本点不动」的缺陷用例用：add_to_cart 内部会等角标 +1，
        按钮失效时那条等待会白等满 10 秒，报出来只有一个超时。
        """
        self._click(self._card_button_locator(title, order))

    def button_text(self, title, order="add"):
        return self._text(self._card_button_locator(title, order))

    #获取列表页面中已在购物车的商品
    def get_card_product_from_page(self):
        products_list = self.get_all_products_title_and_price_and_img()
        products_in_cart_list = []
        for item in products_list:
            locator = (By.CSS_SELECTOR, f'[data-test="remove-{item[0].lower().replace(" ", "-")}"]')
            if self.driver.find_elements(*locator):
                products_in_cart_list.append((item[0], item[1]))

        return products_in_cart_list

    

        



        