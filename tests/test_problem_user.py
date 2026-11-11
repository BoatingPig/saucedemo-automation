"""已知缺陷用例：同一条断言跑两个账号，standard_user 通过、problem_user 预期失败。

为什么需要这个文件：项目对 standard_user 是全绿的，说明代码里没有客观存在的缺陷。
而 xfail 要有"预期正确、现实不满足"的用例才能演示，SauceDemo 站方提供的几个
预置了异常行为的账号正好充当缺陷源。

报告里应该成对出现：

    test_last_name_can_be_typed[standard_user]                PASSED
    test_last_name_can_be_typed[problem_user]                 XFAIL

三条纪律：

1. 断言只写一份，两个账号共用。standard_user 那一侧必须绿 —— 它红了说明
   用例本身写错了，这时候该改代码，不该去改 xfail。
2. 不给 test_checkout.py 这类功能用例加账号参数化。logged_in_driver 是所有
   fixture 的根，挂在那里等于整个项目乘以账号数（44 条会变 220 条）。
3. reason 里如实写明这是站方预置的故障样本。它模拟缺陷，但不是意外缺陷，
   写清楚反而不减分 —— 说明你知道自己在演示什么。
"""

import pytest

from pages.checkout_page import CheckoutInfoPage
from pages.list_page import ListPage


STANDARD_USER = "standard_user"
PROBLEM_USER = "problem_user"

# problem_user 下点了没反应的三件商品（Backpack / Bike Light / Onesie 是正常的）
BROKEN_ADD_TITLES = [
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Fleece Jacket",
    "Test.allTheThings() T-Shirt (Red)",
]

# problem_user 下三种排序全都不生效
SORT_VALUES = ["za", "lohi", "hilo"]

DRIFT_NOTE = "（SauceDemo 站方预置的故障样本，用于演示缺陷登记流程）"


def two_accounts(reason):
    """构造参数表：[standard_user, problem_user(挂 xfail)]。

    对照组和缺陷实例在同一个用例里，所以断言只维护一份。
    strict=True 的意义：缺陷哪天被"修好"，这条会变成 XPASS 并且报红，
    提醒你回来摘标记 —— 那是唯一能在"问题消失"时主动通知你的机制。
    """
    return [
        STANDARD_USER,
        pytest.param(
            PROBLEM_USER,
            marks=pytest.mark.xfail(strict=True, reason=reason),
        ),
    ]


@pytest.mark.parametrize(
    "logged_in_driver",
    two_accounts(
        "DEF-101 problem_user 结算页姓氏输入框焦点错位："
        "往 lastName 输入 Zhang 后，firstName 变成 'g'、lastName 为空；"
        "standard_user 下 lastName 正确为 Zhang。" + DRIFT_NOTE
    ),
    indirect=True,
)
def test_last_name_can_be_typed(checkout_info_driver):
    """姓氏框能接住输入的内容，且不会污染名字框。"""
    page = CheckoutInfoPage(checkout_info_driver)
    page.fill_info("", "Zhang", "100000")

    assert page.get_input_values() == {
        "firstName": "",
        "lastName": "Zhang",
        "postalCode": "100000",
    }


@pytest.mark.parametrize("sort_value", SORT_VALUES)
@pytest.mark.parametrize(
    "logged_in_driver",
    two_accounts(
        "DEF-102 problem_user 商品排序不生效："
        "选择 za / lohi / hilo 后列表顺序完全不变；"
        "standard_user 下切换后首项立即改变。" + DRIFT_NOTE
    ),
    indirect=True,
)
def test_sort_takes_effect(logged_in_driver, sort_value):
    """选完排序后，列表顺序应该发生变化。"""
    page = ListPage(logged_in_driver)
    titles_before = page.get_all_products_title()

    page.select_sort_value(sort_value)

    assert page.sort_order_changed(titles_before), (
        f"选择 {sort_value} 后列表顺序没有变化"
    )


@pytest.mark.parametrize(
    "title", BROKEN_ADD_TITLES, ids=["bolt-tshirt", "fleece-jacket", "red-tshirt"]
)
@pytest.mark.parametrize(
    "logged_in_driver",
    two_accounts(
        "DEF-103 problem_user 部分商品加购按钮无效："
        "Bolt T-Shirt / Fleece Jacket / Test.allTheThings() T-Shirt (Red) 三件"
        "点 Add to cart 后角标不变；Backpack / Bike Light / Onesie 正常。"
        + DRIFT_NOTE
    ),
    indirect=True,
)
def test_add_to_cart_button_works(logged_in_driver, title):
    """点加购按钮，角标应该增加。"""
    page = ListPage(logged_in_driver)
    before = page.cart_count()

    page.click_card_button(title, "add")

    assert page.cart_count_changed(before), (
        f"点 {title} 的 Add to cart 后角标没有变化"
    )


@pytest.mark.parametrize(
    "logged_in_driver",
    two_accounts(
        "DEF-104 problem_user 购物车移除按钮无效："
        "Backpack 加购成功（角标 1），点 Remove 后角标仍为 1、商品行不消失；"
        "standard_user 下角标归 0。" + DRIFT_NOTE
    ),
    indirect=True,
)
def test_remove_from_cart_button_works(cart_had_product_driver):
    """点移除按钮，角标应该减少。"""
    page = ListPage(cart_had_product_driver)
    before = page.cart_count()

    page.click_card_button("Sauce Labs Backpack", "remove")

    assert page.cart_count_changed(before), "点 Remove 后购物车角标没有变化"
