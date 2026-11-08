from pages.list_page import ListPage
import pytest
from data.expected_products import EXPECTED_PRODUCTS
from conftest import DEFAULT_PRODUCT_TITLE
import random

RANDOM_TITLES = random.sample([item[0] for item in EXPECTED_PRODUCTS], 3)


# 加购后验证卡片按钮，角标
@pytest.mark.parametrize("title", [item[0] for item in EXPECTED_PRODUCTS], ids=[item[0] for item in EXPECTED_PRODUCTS])
def test_add_to_cart(logged_in_driver, title):
    list_page = ListPage(logged_in_driver)

    before_cart_count = list_page.cart_count()
    
    list_page.add_to_cart(title)

    after_cart_count = list_page.cart_count()

    # 点击之后，断言
    assert list_page.check_button_text(title, order="remove")

    assert after_cart_count - before_cart_count == 1


def test_remove_from_cart(cart_had_product_driver):
    list_page = ListPage(cart_had_product_driver)
    title = DEFAULT_PRODUCT_TITLE
    
    before_cart_count = list_page.cart_count()
    list_page.remove_from_cart(title)

    after_cart_count = list_page.cart_count()

    assert list_page.check_button_text(title, order="add")
    
    assert before_cart_count - after_cart_count == 1

    assert after_cart_count == 0

@pytest.mark.parametrize("title_list", [RANDOM_TITLES], ids=["three_random_items"])
def test_add_multiple_items(logged_in_driver, title_list):
    list_page = ListPage(logged_in_driver)
    
    for title in title_list:
        before_cart_count = list_page.cart_count()
        list_page.add_to_cart(title)
        after_cart_count = list_page.cart_count()

        assert list_page.check_button_text(title, order="remove")
        assert after_cart_count - before_cart_count == 1
    
