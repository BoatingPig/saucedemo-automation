import pytest

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
def test_checkout_requires_all_fields(
    checkout_info_driver, first_name, last_name, postal_code, expected_error
):
    """收货信息三个字段都必填，缺哪个就报哪个，且不跳转"""
    page = CheckoutInfoPage(checkout_info_driver)

    error = page.submit_info_expect_error(first_name, last_name, postal_code)

    assert error == expected_error
    # 校验失败时应该留在第一步，不能被放行到下一步
    assert "checkout-step-one.html" in checkout_info_driver.current_url


@pytest.mark.parametrize("cart_with_n_items", [1, 2], indirect=True)
def test_checkout_subtotal_equals_item_sum(checkout_overview_driver):
    """小计 == 清单里所有商品价格之和"""
    page = CheckoutOverviewPage(checkout_overview_driver)

    prices = page.get_row_prices()

    assert prices, "结算页上没有商品，前置条件没生效"
    assert page.get_subtotal() == pytest.approx(sum(prices), abs=0.01)


@pytest.mark.parametrize("cart_with_n_items", [1, 2], indirect=True)
def test_checkout_total_equals_subtotal_plus_tax(checkout_overview_driver):
    """总额 == 小计 + 税

    注意不能写成 total == subtotal + tax：
    39.98 + 3.20 在 Python 里是 43.18000000000001，直接比会挂。
    金额比较一律用 pytest.approx。
    """
    page = CheckoutOverviewPage(checkout_overview_driver)

    subtotal = page.get_subtotal()
    tax = page.get_tax()
    total = page.get_total()

    assert subtotal > 0
    assert tax > 0
    assert total == pytest.approx(subtotal + tax, abs=0.01)


@pytest.mark.parametrize("cart_with_n_items", [1, 3], indirect=True)
def test_checkout_overview_matches_cart(cart_with_n_items):
    """结算页的商品名和价格，与购物车页一致（跨页面一致性）"""
    list_page = ListPage(cart_with_n_items)
    list_page.go_to_cart()

    cart_page = CartPage(cart_with_n_items)
    cart_rows = cart_page.get_title_and_price_from_rows(cart_page.get_all_rows())

    cart_page.click_checkout()
    CheckoutInfoPage(cart_with_n_items).submit_info(**DEFAULT_CHECKOUT_INFO)

    overview = CheckoutOverviewPage(cart_with_n_items)

    # 左边是购物车页读的，右边是结算页读的，两边都是页面真实数据
    assert overview.get_row_names() == [title for title, _ in cart_rows]
    assert overview.get_row_prices() == pytest.approx(
        [parse_money(price) for _, price in cart_rows], abs=0.01
    )


def test_checkout_finish_clears_cart(checkout_overview_driver):
    """下单完成后显示完成页，并且购物车被清空（角标消失）"""
    CheckoutOverviewPage(checkout_overview_driver).click_finish()

    complete = CheckoutCompletePage(checkout_overview_driver)
    assert complete.get_header_text() == "Thank you for your order!"
    assert complete.cart_count() == 0


def test_checkout_overview_cancel_returns_to_list(checkout_overview_driver):
    """第二步点 Cancel 回到商品列表页"""
    CheckoutOverviewPage(checkout_overview_driver).click_cancel()

    assert "inventory.html" in checkout_overview_driver.current_url
