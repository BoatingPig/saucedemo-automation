# SauceDemo UI Automation

基于 Selenium + pytest 的 Web UI 自动化测试项目，被测站点为 [SauceDemo](https://www.saucedemo.com/) —— Sauce Labs 提供的电商练习站点，覆盖登录、商品列表、购物车、结算的完整下单链路。

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
├── conftest.py              # fixture：浏览器生命周期、已登录状态
├── pages/                   # 页面对象层（定位器 + 业务动作）
│   ├── base_page.py         # 公共能力：等待、输入、点击、取文本、取元素列表
│   ├── login_page.py        # 登录页
│   └── list_page.py         # 商品列表页
├── tests/                   # 用例层（只做断言，不含定位器）
│   ├── test_login.py        # 登录 9 条（CSV 参数化）
│   └── test_list.py         # 商品列表 5 条
└── data/
    └── login_cases.csv      # 登录场景数据
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

## 覆盖范围

### 已完成（14 条）

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

**商品列表（5 条）**

| 用例 | 断言 |
|---|---|
| 默认商品数据 | 6 组 `(名称, 价格)` 与期望列表完全一致，含 A-Z 顺序 |
| 商品卡片数量 | 数量为 6 |
| 图片渲染 | 6 张图片 `naturalWidth > 0`（轮询 `img.complete` 后判定） |
| 购物车图标跳转 | 点击后进入 `cart.html` |
| 登录后跳转 | 已登录状态停留在列表页 |

### 规划中

- 排序：`za` / `lohi` / `hilo` 三种规则，期望值按同一规则重算后整体比对
- 购物车：加购与移除、角标计数、角标为 0 时节点消失、刷新后状态保留
- 跨页面一致性：同一商品在列表页、详情页、购物车页、结算页的名称与价格一致
- 缺陷专项：用 `problem_user` / `visual_user` 等故障注入账号验证用例的缺陷检出能力，标记 `xfail(strict=True)`

## 设计说明

**1. 定位统一用 `data-test` 属性**

SauceDemo 为每个交互元素保留了 `data-test` 钩子（如 `[data-test="username"]`），它是专门给自动化用的，不会随样式改版变动。全项目未使用层级 XPath（如 `div > div:nth-child(3)`），避免页面加个广告位就全线失效。

**2. 只用显式等待**

等待条件封装在 `BasePage` 里，业务代码通过 `self._click`、`self._type` 调用，不在用例中散落 `WebDriverWait`。未设置 `implicitly_wait`——隐式等待与显式等待叠加会产生不可预测的实际超时，排查困难。

图片加载这类非 DOM 就绪条件，用 JS 轮询 `img.complete` 而非固定 `sleep`：加载快时立即返回，慢时自动延长，不做无意义等待。

**3. 商品数据按卡片读取，不拆成独立列表**

```python
for card in cards:
    name = card.find_element(*self.PRODUCT_TITLE).text
    price = card.find_element(*self.PRODUCT_PRICE).text
    result.append((name, price))
```

如果分别取「名称列表」和「价格列表」再比对，两个列表各自都可能正确，但配对关系错了检不出来。以卡片为最小单位读取，能捕获价格串位这类缺陷。

**4. 登录作为前置条件，抽成 fixture**

`logged_in_driver` 完成「打开登录页 → 输入账号 → 点击登录 → 等待 URL 跳转 → 等待商品卡片渲染」整条链路。用例中不出现任何登录步骤，读代码时直接看到业务动作。

**5. 用例之间不做状态共享**

`driver` 为 `function` 作用域，每条用例独立启动浏览器。代价是每次多 1-2 秒，收益是购物车残留、登录态污染这类最难排查的失败不会出现。用例数量增长后如需优化，优先考虑 `Reset App State` 而非共享浏览器。

## 已知限制

- 仅适配 Edge（Chromium），未做跨浏览器验证
- 尚未接入 CI（GitHub Actions）与 HTML 测试报告
- SauceDemo 无后端接口，商品数据硬编码在前端 JS bundle 中，因此未做「接口 vs 页面」的数据一致性校验，跨页一致性改由页面之间互相校验

## 被测站点的已知缺陷

SauceDemo 提供多个故障注入账号（密码统一 `secret_sauce`），用于验证测试用例的检出能力：

| 账号 | 缺陷表现 |
|---|---|
| `locked_out_user` | 无法登录 |
| `problem_user` | 商品图片全部错配、排序失效、结算时无法提交 |
| `performance_glitch_user` | 登录后响应延迟 5 秒以上 |
| `error_user` | 表单校验失效、Finish 按钮无响应 |
| `visual_user` | 元素错位、价格每次交互后漂移 |

针对这些账号的用例将以 `xfail(strict=True)` 标记：缺陷存在时测试保持绿色（标记为预期失败），一旦站点修复会转为 `XPASS` 并报红，提示更新用例。
