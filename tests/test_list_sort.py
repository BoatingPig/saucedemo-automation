from pages.list_page import ListPage
from selenium.webdriver.support.ui import Select

SORT_NAME_ASC = "az"
SORT_NAME_DESC = "za"
SORT_PRICE_ASC = "lohi"
SORT_PRICE_DESC = "hilo"

#测试商品列表页默认商品名排序是不是按a-z
def test_default_sort_is_az(logged_in_driver):
    list_page = ListPage(logged_in_driver)

    cards_list = list_page.get_all_products_title_and_price_and_img()
    assert len(cards_list) == 6
    assert list_page.check_sort_products(cards_list, target="title", order="asc")



#测试商品名按z-a排列功能
def test_sort_name_desc(logged_in_driver):
    #首先要登录，并进入商品页面-logged in driver
    #对排序下拉输入框，输入商品名z-a，并请求
    #拿到当前所有的商品卡片，获取信息
    #对拿到的信息拆成title列表，并验证是不是按z-a进行排序
    #断言：是要设计，
    #1.商品名按z-a排序，
    #2.排序后商品名与价格仍是一致的

    list_page = ListPage(logged_in_driver)
    list_page.click_sort_select_value(SORT_NAME_DESC)

    cards_list = list_page.get_all_products_title_and_price_and_img()
    assert len(cards_list) == 6
    assert list_page.check_sort_products(cards_list, target="title", order="desc")

def test_sort_price_asc(logged_in_driver):
    list_page = ListPage(logged_in_driver)
    list_page.click_sort_select_value(SORT_PRICE_ASC)
    
    cards_list = list_page.get_all_products_title_and_price_and_img()
    assert len(cards_list) == 6
    assert list_page.check_sort_products(cards_list, target="price", order="asc")

def test_sort_price_desc(logged_in_driver):
    list_page = ListPage(logged_in_driver)
    list_page.click_sort_select_value(SORT_PRICE_DESC)
        
    cards_list = list_page.get_all_products_title_and_price_and_img()
    assert len(cards_list) == 6
    assert list_page.check_sort_products(cards_list, target="price", order="desc")

    
        



    
