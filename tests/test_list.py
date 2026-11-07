from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.list_page import ListPage

# 基础冒烟：
# 1.登录后正常跳转，inventory.html 在 URL 中
# 2.页面标题，文本 == Products
# 3.卡片数量，== 6
# 4.购物车图片可点击，点击后进入 /cart.html


EXPECTED_PRODUCTS = [
    ("Sauce Labs Backpack",                 "$29.99"),
    ("Sauce Labs Bike Light",               "$9.99"),
    ("Sauce Labs Bolt T-Shirt",             "$15.99"),
    ("Sauce Labs Fleece Jacket",            "$49.99"),
    ("Sauce Labs Onesie",                   "$7.99"),
    ("Test.allTheThings() T-Shirt (Red)",   "$15.99"),
]

CARDS_COUNT = 6

def test_login_redirects_to_url(logged_in_driver):
    # 登录后进入，需要有一个前置
    assert "inventory.html" in logged_in_driver.current_url

def test_default_products_data(logged_in_driver):
    #从driver里拿元素与期望值进行比对
    #默认当前在列表页中
    #直接拿取所有商品的标题名好了
    #2.0加上价格
    list_page = ListPage(logged_in_driver)
    list_product = list_page.get_all_products_title_and_price_and_img()

    list_title_price = [(item[0], item[1]) for item in list_product]

    #比较
    assert list_title_price == EXPECTED_PRODUCTS

def test_product_card_count(logged_in_driver):
    list_page = ListPage(logged_in_driver)
    elements_count = list_page.get_product_cards_count()
    assert elements_count == CARDS_COUNT

def test_cart_icon_opens_cart_page(logged_in_driver):
    list_page = ListPage(logged_in_driver)
    list_page.go_to_cart()
    assert "cart.html" in logged_in_driver.current_url

def test_product_images_loaded(logged_in_driver):
    #其实没有真实数据去验证图片和商品信息是否一致，只是简单看一下图片能否正确的渲染出来了。
    list_page = ListPage(logged_in_driver)
    list_product = list_page.get_all_products_title_and_price_and_img()

    imges = [element[2] for element in list_product]
    list_page.wait_img_loaded(imges)

    for item in list_product:
        img_element = item[2]
        nature_width = img_element.get_attribute("naturalWidth")
        # print("yhy debug" + str(type(nature_width)))

        if nature_width and nature_width is not None:
            assert int(nature_width) > 0
        else:
            # print("yhy debug " + str(img_element.get_attribute("src")))
            # print("yhy debug " + item[0])
            assert False,"img nature width is NONE"

        

    