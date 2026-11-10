import pytest
import math

from conftest import DEFAULT_CHECKOUT_INFO
from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
    parse_money,
)
from pages.list_page import ListPage


# 三个必填字段各缺一次：一次参数化顶三条用例
REQUIRED_FIELD_CASES = [
    ("", "Zhang", "100000", "Error: First Name is required"),
    ("San", "", "100000", "Error: Last Name is required"),
    ("San", "Zhang", "", "Error: Postal Code is required"),
]
REQUIRED_FIELD_IDS = ["no_first_name", "no_last_name", "no_postal_code"]


@pytest.mark.parametrize(
    "first_name, last_name, postal_code, expected_error",
    REQUIRED_FIELD_CASES,
    ids=REQUIRED_FIELD_IDS,
)
def test_checkout_requires_all_fields(checkout_info_driver, first_name, last_name, postal_code, expected_error):

    chcekout_page = CheckoutInfoPage(checkout_info_driver)
    # 填写。
    ret = chcekout_page.submit_info_expect_error(first_name, last_name, postal_code)

    assert ret == expected_error

    assert chcekout_page.URL in checkout_info_driver.current_url


@pytest.mark.parametrize("cart_with_n_items", [1, 2], indirect=True)
def test_checkout_subtotal_equals_item_sum(checkout_overview_driver):

    checkout_overview_page = CheckoutOverviewPage(checkout_overview_driver)
    price_list = checkout_overview_page.get_row_prices()

    assert len(price_list) > 0

    row_price = sum(price_list)
    subtotal_price = checkout_overview_page.get_subtotal()

    assert math.isclose(row_price, subtotal_price)
    

@pytest.mark.parametrize("cart_with_n_items", [1, 2], indirect=True)
def test_checkout_total_equals_subtotal_plus_tax(checkout_overview_driver):

    checkout_overview_page = CheckoutOverviewPage(checkout_overview_driver)

    subtotal_price = checkout_overview_page.get_subtotal()
    tax_price = checkout_overview_page.get_tax()
    total_price = checkout_overview_page.get_total()

    assert math.isclose(subtotal_price+tax_price, total_price)

    
@pytest.mark.parametrize("cart_with_n_items", [1, 3], indirect=True)
def test_checkout_overview_matches_cart(cart_with_n_items):

    list_page = ListPage(cart_with_n_items)
    list_page.go_to_cart()

    cart_page = CartPage(cart_with_n_items)
    cart_products = cart_page.get_title_and_price_from_rows(cart_page.get_all_rows())
    cart_page.click_checkout()

    checkout_info = CheckoutInfoPage(cart_with_n_items)
    checkout_info.submit_info(**DEFAULT_CHECKOUT_INFO)

    checkout_overview = CheckoutOverviewPage(cart_with_n_items)
    checkout_products_name = checkout_overview.get_row_titles()
    checkout_products_price = checkout_overview.get_row_prices()

    assert checkout_products_name == [product[0] for product in cart_products]

    assert checkout_products_price == [parse_money(product[1]) for product in cart_products]


def test_checkout_finish_clears_cart(checkout_overview_driver):

    checkout_overview = CheckoutOverviewPage(checkout_overview_driver)
    checkout_overview.click_finish()
    checkout_complete_page = CheckoutCompletePage(checkout_overview_driver)
    
    assert checkout_complete_page.get_header_text() == "Thank you for your order!"

    assert checkout_complete_page.cart_count() == 0


def test_checkout_overview_cancel_returns_to_list(checkout_overview_driver):

    checkout_overview = CheckoutOverviewPage(checkout_overview_driver)
    overview_titles = checkout_overview.get_row_titles()
    overview_price = checkout_overview.get_row_prices()

    checkout_overview.click_cancel()

    list_page = ListPage(checkout_overview_driver)
    card_products = list_page.get_card_product_from_page()

    assert "inventory.html" in checkout_overview_driver.current_url

    assert overview_titles == [product[0] for product in card_products]

    assert overview_price == [parse_money(product[1]) for product in card_products]
    
