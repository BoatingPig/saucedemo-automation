# SauceDemo UI Automation

基于 Selenium + pytest 的 Web UI 自动化测试项目，被测站点为 [SauceDemo](https://www.saucedemo.com/) —— Sauce Labs 提供的电商练习站点，覆盖登录、商品列表、排序、购物车、结算的完整下单链路。

## 技术栈

| 用途 | 选型 |
|---|---|
| 语言 | Python 3.12 |
| 浏览器驱动 | Selenium 4.52 |
| 测试框架 | pytest 9.2 |
| 浏览器 | Microsoft Edge（Chromium 内核） |
| 设计模式 | Page Object Model |

## 项目结构

```
WebSeleniumProject/
├── conftest.py                  # fixture：浏览器生命周期、登录态、购物车与结算前置
├── pages/                       # 页面对象层（定位器 + 业务动作，不含断言）
│   ├── base_page.py             # 公共能力：等待、输入、点击、取文本、角标计数
│   ├── login_page.py            # 登录页
│   ├── list_page.py             # 商品列表页：展示、排序、加购与移除
│   ├── cart_page.py             # 购物车页：行数据读取、删除、跳转
│   └── checkout_page.py         # 结算三步：收货信息 / 订单确认 / 下单完成
├── tests/                       # 用例层（只做断言，不含定位器）
│   ├── test_login.py            # 登录，CSV 参数化
│   ├── test_list.py             # 商品列表展示
│   ├── test_list_sort.py        # 商品排序
│   ├── test_list_cart.py        # 列表页加购 / 移除，购物车页
│   ├── test_checkout.py         # 结算流程
│   └── test_problem_user.py     # 已知缺陷专项，xfail 标记
└── data/
    ├── login_cases.csv          # 登录场景数据
    └── expected_products.py     # 商品期望数据：名称、价格、价格排序辅助函数
```

## 环境准备

```bash
git clone https://github.com/BoatingPig/saucedemo-automation.git
cd saucedemo-automation

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

## 运行

```bash
pytest                          # 全部用例
pytest tests/test_login.py -v   # 单模块
pytest -k "cart or image"       # 按名称筛选
pytest --collect-only -q        # 只收集不执行，排查用例未被执行的问题
```

批量输出的三个参数，排查失败时用：

```bash
pytest -q --tb=line -rf         # 精简输出 + 一行报错 + 末尾汇总失败名单
pytest -rx                      # 末尾汇总所有 xfail 及其 reason
pytest --runxfail               # 忽略 xfail 标记，当普通用例跑（自查用）
```

环境变量：

```bash
HEADLESS=1 pytest                       # 无头模式，不弹窗，可以边跑边做别的
SAUCE_USER=problem_user pytest          # 指定登录账号，默认 standard_user
```

Windows PowerShell 写法：`$env:HEADLESS="1"; pytest`

## 覆盖范围

### 已完成（60 条：52 passed + 8 xfailed）

| 模块 | 用例数 | 覆盖内容 |
|---|---|---|
| 登录 | 9 | CSV 数据驱动，正确 / 锁定 / 密码错 / 空值 / 空格 / 大小写 |
| 商品列表 | 5 | 数据与期望完全一致、卡片数量、图片渲染、购物车跳转 |
| 商品排序 | 4 | 默认 A-Z、Z-A、价格升序、价格降序 |
| 购物车 | 15 | 加购、移除、角标计数、空车状态、购物车页与列表页数据一致、继续购物、去结算 |
| 结算 | 11 | 三个必填字段校验、小计、税额与总额、跨页一致性、下单后清空购物车、取消流程 |
| 已知缺陷专项 | 16 | 4 个缺陷 × 双账号对照，8 passed + 8 xfailed |
| **合计** | **60** | 一次执行 4 分 40 秒左右 |

实测结果：

```
52 passed, 8 xfailed in 277.45s        exit code 0
```

### 单模块要点

**登录（9 条，CSV 数据驱动）**

| 场景 | 预期 |
|---|---|
| 正常登录 | 跳转 `inventory.html` |
| 账号锁定 | `locked out` |
| 密码错误 | `do not match` |
| 用户名 / 密码为空 | `Username is required` / `Password is required` |
| 账号含前后空格 | 登录失败 |
| 账号 / 密码大小写不匹配 | 登录失败 |

每条用例只改变一个变量（例如验证大小写敏感时，密码保持完全正确），保证失败时可归因。

**购物车（15 条）**

覆盖两处位置：列表页的加购/移除按钮，和购物车页本身。核心是跨页一致性——列表页读一次、购物车页读一次，两个页面的真实数据整体比对，不用硬编码。

**结算（11 条）**

三个步骤拆成三个页面对象（`CheckoutInfoPage` / `CheckoutOverviewPage` / `CheckoutCompletePage`）。金额断言用 `pytest.approx(..., abs=0.01)`，因为 `39.98 + 3.20` 在 Python 里是 `43.18000000000001`。

## 设计说明

**1. 定位统一用 `data-test` 属性**

SauceDemo 为每个交互元素保留了 `data-test` 钩子（如 `[data-test="username"]`），它是专门给自动化用的，不会随样式改版变动。全项目未使用层级 XPath（如 `div > div:nth-child(3)`），避免页面加个广告位就全线失效。

**2. 只用显式等待**

等待条件封装在 `BasePage` 里，业务代码通过 `self._click`、`self._type` 调用，不在用例中散落 `WebDriverWait`。未设置 `implicitly_wait`——隐式等待与显式等待叠加会产生不可预测的实际超时，排查困难。

图片加载这类非 DOM 就绪条件，用 JS 轮询 `img.complete` 而非固定 `sleep`：加载快时立即返回，慢时自动延长，不做无意义等待。

**3. 「一定有」用带等待的封装，「可能有」用 `find_elements`**

`_get_all_element` 内部是 `visibility_of_all_elements_located`，匹配到 0 个元素时会等满 10 秒再抛超时。所以凡是「数量可能为 0」的地方（空购物车的行数、购物车角标、未加购商品有没有 Remove 按钮）一律走 `find_elements`，找不到返回空列表，立即得到结果。

**4. 商品数据按卡片读取，不拆成独立列表**

```python
for card in cards:
    name = card.find_element(*self.PRODUCT_TITLE).text
    price = card.find_element(*self.PRODUCT_PRICE).text
    result.append((name, price))
```

如果分别取「名称列表」和「价格列表」再比对，两个列表各自都可能正确，但配对关系错了检不出来。以卡片为最小单位读取，能捕获价格串位这类缺陷。

**5. 跨页一致性：两个页面各自从 DOM 读，整体比对**

```python
assert cart_rows == list_page.get_card_product_from_page()
```

两边都不碰硬编码，各读各的 DOM。这种写法的失败信息是逐项 diff，哪个商品错位一眼能看出来；而逐个 `assert` 的循环在列表为空时会一次都不执行，变成假通过。

**6. 登录作为前置条件，抽成 fixture**

`logged_in_driver` 完成「打开登录页 → 输入账号 → 点击登录 → 等待 URL 跳转 → 等待商品卡片渲染」整条链路。用例中不出现任何登录步骤，读代码时直接看到业务动作。

同一套 fixture 链向上叠加：`cart_with_n_items`（购物车有 N 件）→ `checkout_info_driver`（停在结算第一步）→ `checkout_overview_driver`（停在第二步）。前置条件失败时 fixture 内 `assert`，pytest 报 `ERROR` 而不是 `FAILED`，一眼区分「环境没准备好」和「功能有 bug」。

**7. 用例之间不做状态共享**

`driver` 为 `function` 作用域，每条用例独立启动浏览器。代价是每次多 1-2 秒，收益是购物车残留、登录态污染这类最难排查的失败不会出现。用例数量增长后如需优化，优先考虑 `Reset App State` 而非共享浏览器。

## 已知缺陷管理

SauceDemo 提供若干故障注入账号（密码统一 `secret_sauce`），用来模拟「同一份功能在特定条件下失效」的场景。项目用 `problem_user` 作为缺陷源，每个缺陷写一条最小复现用例，同一条断言同时跑 `standard_user`（对照组，必须通过）和 `problem_user`（挂 `xfail`，预期失败）。

```python
@pytest.mark.parametrize("logged_in_driver", [
    "standard_user",
    pytest.param("problem_user", marks=pytest.mark.xfail(strict=True, reason="DEF-101 ...")),
], indirect=True)
def test_last_name_can_be_typed(checkout_info_driver):
    ...
```

断言只维护一份，两个账号共用。`standard_user` 那一侧必须绿——它红了说明用例本身写错了，这时候该改代码，不该去改 xfail。

| 单号 | 缺陷现象 | 对应用例 | 状态 |
|---|---|---|---|
| DEF-101 | 结算页姓氏输入框焦点错位：往姓氏框输入 `Zhang`，内容跑进名字框且只保留最后一个字符 `g` | `test_last_name_can_be_typed` | `xfail` |
| DEF-102 | 商品排序不生效：选择 `za` / `lohi` / `hilo` 后列表顺序完全不变 | `test_sort_takes_effect` | `xfail` |
| DEF-103 | 部分商品加购按钮无效：Bolt T-Shirt、Fleece Jacket、Test.allTheThings() T-Shirt (Red) 三件点击后角标不变（其余三件正常） | `test_add_to_cart_button_works` | `xfail` |
| DEF-104 | 购物车移除按钮失效：点 `Remove` 后角标仍为 1，商品行不消失 | `test_remove_from_cart_button_works` | `xfail` |

全部标记为 `xfail(strict=True)`：缺陷存在时用例计为 `XFAIL`、不影响退出码；站点修复后转为 `XPASS` 并报红，提示回来摘除标记。

`strict=True` 是必需的。没有它，缺陷被修复后用例变成 `XPASS`，报告是黄色但退出码仍是 0，CI 继续绿，没人会去摘标记——那条用例从此退化成「什么都不验证」，将来同一处再坏也不会被发现。

### 两个未标记 xfail 的账号，及原因

| 账号 | 行为 | 为什么不用 xfail |
|---|---|---|
| `locked_out_user` | 登录被拒绝，提示 `Sorry, this user has been locked out` | 这是**需求规定的行为**，不是缺陷。已在 `test_login.py` 作为正常用例断言错误文案 |
| `performance_glitch_user` | 登录后每个动作延迟 5 秒以上 | 这是**性能场景**，不是功能缺陷。应用更长的超时配置验证链路是否仍能跑通，标 xfail 会掩盖「超时设置是否合理」这个真问题 |

判断标准：**这条用例的断言写对了吗？如果被测系统是完美的，它会通过吗？**

会通过 → 是缺陷，标 `xfail`；不会通过 → 是用例本身的问题，去改代码。设计上就该失败的行为（如锁定账号登不进去）不属于缺陷，标 xfail 等于承认自己误读了需求。

### 自查

```bash
pytest tests/test_problem_user.py --runxfail -q --tb=line
```

忽略标记重跑一遍，用来确认这些用例失败的原因是 `AssertionError`（产品缺陷），而不是 `TimeoutException` / `NoSuchElementException`（用例自己坏了）。xfail 只判断「失败了」，不判断「为什么失败」，两者在正常报告里长得完全一样。

## 已知限制

- 仅适配 Edge（Chromium），未做跨浏览器验证
- 尚未接入 CI（GitHub Actions）与 HTML 测试报告
- 未覆盖商品详情页
- SauceDemo 无后端接口，商品数据硬编码在前端 JS bundle 中，因此未做「接口 vs 页面」的数据一致性校验，跨页一致性改由页面之间互相校验
