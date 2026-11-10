from pages.list_page import ListPage
import pytest
from data.expected_products import EXPECTED_PRODUCTS
from conftest import DEFAULT_PRODUCT_TITLE
import random
from pages.cart_page import CartPage

RANDOM_TITLES = random.sample([item[0] for item in EXPECTED_PRODUCTS], 3)


# 加购后验证卡片按钮，角标
@pytest.mark.parametrize("title", [item[0] for item in EXPECTED_PRODUCTS], ids=[item[0] for item in EXPECTED_PRODUCTS])
def test_add_to_cart(logged_in_driver, title):
    list_page = ListPage(logged_in_driver)

    before_cart_count = list_page.cart_count()
    
    list_page.add_to_cart(title)

    after_cart_count = list_page.cart_count()

    # 点击之后，断言
    assert list_page.button_text(title, order="remove") == ListPage.REMOVE_BTN_TEXT

    assert after_cart_count - before_cart_count == 1


def test_remove_from_cart(cart_had_product_driver):
    list_page = ListPage(cart_had_product_driver)
    title = DEFAULT_PRODUCT_TITLE
    
    before_cart_count = list_page.cart_count()
    list_page.remove_from_cart(title)

    after_cart_count = list_page.cart_count()

    assert list_page.button_text(title, order="add") == ListPage.ADD_BTN_TEXT
    
    assert before_cart_count - after_cart_count == 1

    assert after_cart_count == 0

@pytest.mark.parametrize("title_list", [RANDOM_TITLES], ids=["three_random_items"])
def test_add_multiple_items(logged_in_driver, title_list):
    list_page = ListPage(logged_in_driver)
    
    for title in title_list:
        before_cart_count = list_page.cart_count()
        list_page.add_to_cart(title)
        after_cart_count = list_page.cart_count()

        assert list_page.button_text(title, order="remove") == ListPage.REMOVE_BTN_TEXT
        assert after_cart_count - before_cart_count == 1
    
def test_cart_shows_added_product(cart_had_product_driver):
    # 已经在商品页加购了一个商品，命名为DEFAULT_PRODUCT_TITLE
    # 验证

    # 先看看当前列表里，有什么被加到了购物车里的
    # 一般是通过后端拿数据库里看真实购物车里落库的数据
    # 现在只能用参数化的方式驱动
    list_page = ListPage(cart_had_product_driver)
    list_page.go_to_cart()

    cart_page = CartPage(cart_had_product_driver)
    rows = cart_page.get_all_rows()

    # 验证只有一行
    assert len(rows) == 1

    # 验证row里的商品和价格是对应的
    expect_dict = dict(EXPECTED_PRODUCTS)
    products_list = cart_page.get_title_and_price_from_rows(rows)

    for item in products_list:
        assert item[0] == DEFAULT_PRODUCT_TITLE
        assert item[1] == expect_dict[DEFAULT_PRODUCT_TITLE]
        
def test_cart_product_matches_list_page(cart_had_product_driver):
    list_page = ListPage(cart_had_product_driver)
    products_from_page = list_page.get_card_product_from_page()
    list_page.go_to_cart()
    
    cart_page = CartPage(cart_had_product_driver)
    rows = cart_page.get_all_rows()
    products_from_cart = cart_page.get_title_and_price_from_rows(rows)

    assert products_from_cart == products_from_page

def test_cart_badge_matches_row_count(cart_had_product_driver):
    #
    list_page = ListPage(cart_had_product_driver)
    list_page.go_to_cart()

    cart_page = CartPage(cart_had_product_driver)
    rows_len = len(cart_page.get_all_rows())

    cart_count = cart_page.cart_count()

    assert rows_len == cart_count

def test_remove_item_clears_row(cart_had_product_driver):
    list_page = ListPage(cart_had_product_driver)
    list_page.go_to_cart()

    cart_page = CartPage(cart_had_product_driver)
    before_count = cart_page.cart_count()
    cart_page.remove_product(DEFAULT_PRODUCT_TITLE)

    assert before_count - cart_page.cart_count() == 1

    assert cart_page.get_row_count() == 0

def test_continue_shopping_returns_to_list(cart_had_product_driver):
    list_page = ListPage(cart_had_product_driver)
    list_page.go_to_cart()
    cart_page = CartPage(cart_had_product_driver)
    cart_page.click_continue_shopping()

    assert "inventory.html" in cart_had_product_driver.current_url

def test_empty_cart_has_no_rows(logged_in_driver):
    list_page = ListPage(logged_in_driver)
    list_page.go_to_cart()
    cart_page = CartPage(logged_in_driver)
    assert cart_page.get_row_count() == 0

    assert cart_page.cart_count() == 0

def test_checkout_button_opens_step_one(cart_had_product_driver):
    list_page = ListPage(cart_had_product_driver)
    list_page.go_to_cart()
    cart_page = CartPage(cart_had_product_driver)
    cart_page.click_checkout()

    assert "checkout-step-one.html" in cart_had_product_driver.current_url





    

    
    
    





