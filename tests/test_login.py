from pages.login_page import LoginPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pytest

from pathlib import Path
import csv

# 如果同一个功能需要多次输入不同的数据来完成测试，即跑多条测试数据
# 可以用参数化测试函数

DATA_FILE = Path(__file__).parent.parent / "data" / "login_cases.csv"

def load_login_cases():
    with open(DATA_FILE, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

cases = load_login_cases()

temp_cases = [
    {"case_name": "临时测试_密码错误", "username": "locked_out_user", "password": "secret_sauce", "expected": "locked out"}
]

@pytest.mark.parametrize(
        "case",
        cases,
        ids=[c["case_name"] for c in cases]
)
def test_login(driver, case):
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(case["username"], case["password"])

    if not case["expected"]:
        WebDriverWait(driver, 10).until(expected_conditions.url_contains("inventory.html"))
    else:
        assert case["expected"] in login_page.error_msg()


