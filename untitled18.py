看起来既然你在两边都 dump 了原始的 .midway/cookie 文件，内容完全相同，却只有 Brazil 那边用 MozillaCookieJar 只装了两条、本地 Python 能装 13 条，那问题就不在文件本身，而在那颗“解析器”──MozillaCookieJar.load() 在 Brazil 里的 Python3.9 环境中漏掉了大部分条目。

最简单的办法，就是绕开这个不可靠的 loader，自己手写一个小段解析，把每一行都变成一个 requests cookie，然后一股脑儿丢进你的 Session：

python
Copy
Edit
from pathlib import Path
from requests import Session, cookies

def load_midway_cookies_manually(session: Session) -> None:
    cookie_path = Path.home()/".midway"/"cookie"
    if not cookie_path.exists():
        raise FileNotFoundError(f"No midway cookie at {cookie_path!r}")

    jar = cookies.RequestsCookieJar()
    for raw in cookie_path.read_text().splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        # Netscape 格式: domain \t flag \t path \t secure \t expires \t name \t value
        parts = raw.split("\t")
        if len(parts) < 7:
            continue
        domain, _, path, secure_flag, expires, name, value = parts[:7]
        secure = secure_flag.lower() == "true"
        # 去掉开头的点
        if domain.startswith("."):
            domain = domain[1:]
        c = cookies.create_cookie(
            name=name,
            value=value,
            domain=domain,
            path=path,
            secure=secure,
            expires=None if expires in ("0", "") else int(expires),
        )
        jar.set_cookie(c)
    session.cookies = jar
只要调用一次：

python
Copy
Edit
session = Session()
load_midway_cookies_manually(session)
就能保证把文件里所有的 13 条都塞进 session.cookies，不再依赖 MozillaCookieJar.load()。
之后你在 Brazil 上的 SSO 验证、307 重定向就都能带上完整的 cookie，问题自然也就解决了。



看了你最新贴的代码，问题其实出在你那段「手动读文件、跳过 # 行再 create_cookie」的逻辑上。Netscape 格式里，所有带 HttpOnly 标记的 cookie 行都是以 #HttpOnly_… 开头的——并不是注释！你却把一切以 # 开头的行都直接跳过了，结果只解析到那两条不带 HttpOnly 前缀的「普通」cookie。

最简洁的修复方法
直接放弃手写解析，彻底交给 MozillaCookieJar 来做：

python
Copy
Edit
from http.cookiejar import MozillaCookieJar
import requests

def setup_cookies(self):
    cookie_path = Path.home()/".midway"/"cookie"
    jar = MozillaCookieJar(str(cookie_path))
    jar.load(ignore_discard=True, ignore_expires=True)

    # 把所有 cookie 逐条注入 session，而不是 session.cookies.update()
    for c in jar:
        self.session.cookies.set_cookie(c)

    self.logger.debug(f"Total cookies in session: {len(self.session.cookies)}")
这样不管是普通 cookie 还是 #HttpOnly_… 前缀的 HttpOnly cookie，都能被 cookiejar 正确读进来并注入到 requests.Session。

然后把你的 get() 方法里关于 cookies= 的那一段删掉，让 self.session.get() 自己带上完整的 session.cookies：

python
Copy
Edit
def get(self, endpoint: str, **kwargs):
    url = f"{self.base_url}/{endpoint.lstrip('/')}"
    headers = { **self.session.headers, **kwargs.pop("headers", {}) }
    return self.session.get(
        url,
        headers=headers,
        allow_redirects=True,   # 一定要真重定向
        timeout=(5,15),
        **kwargs
    ).json()
这样就不会再“贴”一个只有 2 条的 cookie 集合去覆盖原来的 session，而是把全部 13 条完整地带上，从根本上解决一直被 307 重定向回 SSO 的问题。

如果你还想自己解析文件
那就别把所有 # 行都当注释跳过，而是只跳真正的注释（通常是 # Netscape HTTP Cookie File 之类），保留 #HttpOnly_… 的那些行：

python
Copy
Edit
for line in content:
    if line.startswith("# Netscape"):     # 只跳标准注释头
        continue
    # 接下来不判断 line.startswith('#')，因为 #HttpOnly_ 开头的行才是真 cookie
    fields = line.split("\t")
    # …接着按域名、path、secure、expires、name、value 拆字段…
但既然标准库能一把搞定，就推荐用第一种方案，稳定又少 Bug。这样修改后，你在 Brazil 环境跑，也能一次性拿到完整的 SSO 会话 cookie。















你的思路其实没问题——用 http.cookiejar.MozillaCookieJar 读磁盘，再把它们灌进 requests.Session 的 cookie jar。但是你图里代码处理流程里有两处「隐形过滤」，把 13 条裹进去后又只剩 2 条：

update(cookie_jar) 并不会把所有条目都加到 Session

python
Copy
Edit
cookie_jar = MozillaCookieJar(str(cookie_path))
cookie_jar.load(...)
self.session.cookies.update(cookie_jar)
这一步只会把 cookiejar 里domain、path 完全匹配当前请求域名的几条“默认” cookie 加到 session.cookies；其余那些属于 .auth.midway.amazon.dev、.midway-auth.amazon.com、auth.midway.aws.dev 等域的条目都被丢掉了。

在真正发请求时你又做了二次过滤

python
Copy
Edit
domain_cookies = {
  c.name: c.value
  for c in self.session.cookies
  if target_domain.endswith(c.domain.lstrip('.'))
}
response = self.session.get(..., cookies=domain_cookies)
你只把与 target_domain（corp.management-ui.turtle.aws.dev）严格匹配或后缀匹配的那几条拿出来用，其他域的就都删了。

—— 所以整个流程读进来了 13 条，灌给 session 后只剩能 match 当前 host 的 2 条，再传给 requests.get(..., cookies=…) 时又被精简成 2 条。
👣 改进建议
只要把这两个过滤点拆掉，保留完整的 13 条，就能让后端正确识别你的 SSO 会话：
把完整 cookie_jar 转给 session，而不要用 update
python
Copy
Edit
for cookie in cookie_jar:
    # cookie is a http.cookiejar.Cookie
    self.session.cookies.set_cookie(cookie)
这样不管 domain、path，所有条目都进了 session。

不要在 get() 里再传 cookies=
requests.get(..., cookies=…) 会替你 override 掉 session 里原来的 cookies ，所以把它删掉：
python
Copy
Edit
response = self.session.get(url,
                            headers=headers,
                            allow_redirects=True,
                            timeout=(5,15))
这样，session 发出的每个请求，requests 底层的 HTTP 头里就会自动带上全部 13 条 cookie。你再把 allow_redirects=True 打开，就能绕过一切 307→SSO 的重定向，直接到达真正的 role-mappings API。

项目背景：我们在做一个 Python CLI，用于从公司内部的 React Web UI（路径 /role-mappings-view）抓取 role mappings 数据并支持表格/JSON/CSV 输出。该 UI 受 Midway SSO 保护，登录后会话信息以 13 条 HttpOnly/secure 的 cookie 存在本地 ~/.midway/cookie。

遇到的问题：在本地用 Python 的 http.cookiejar 直接加载磁盘 cookie 并拼到 HTTP 请求头上，可以拿到全部 13 条并成功认证；但在 Amazon 的 Brazil 环境（无头浏览器或前端 JS）里，document.cookie 只能看到 2 条非‑HttpOnly cookie，导致后端始终重定向到 SSO，无法获取数据。

核心思路：先用 Python 读取并序列化那 13 条 cookie 为 JSON，然后在 Brazil/Playwright 中通过 context.add_cookies(...) 注入到浏览器上下文，让所有后续 fetch/XHR 自动带上完整凭证，从而绕过 SSO 重定向，稳定地抓取前端数据。


1. 读取并转换本地 Cookie（在 Python 环境中完成）
用 Python 加载 ~/.midway/cookie

利用标准库 http.cookiejar.MozillaCookieJar（或 http.cookies.SimpleCookie）读出所有条目，包括 HttpOnly。

序列化成纯 JSON 数组

对每个 Cookie 生成一份对象：

json
Copy
Edit
{
  "name": "session",
  "value": "...",
  "domain": "corp.management-ui.turtle.aws.dev",
  "path": "/",
  "httpOnly": true,
  "secure": true,
  "expires": 1690000000
}
把所有对象写到一个临时文件（比如 cookies.json），或直接通过标准输出传给下游脚本。

2. 在 Brazil 中注入并使用这批 Cookie（在 JS/Playwright/Puppeteer 里完成）
启动无头浏览器上下文

js
Copy
Edit
const { chromium } = require("playwright");  // 或 puppeteer
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
加载刚才的 JSON

js
Copy
Edit
const cookies = JSON.parse(fs.readFileSync("cookies.json", "utf8"));
调用 addCookies

js
Copy
Edit
// Playwright:
await context.addCookies(cookies);
js
Copy
Edit
// Puppeteer:
await page.setCookie(...cookies);
这样，即便是 HttpOnly、Secure，浏览器网络层也会自动把它们附到后续所有请求上。

导航到 React 页面

js
Copy
Edit
const page = await context.newPage();
await page.goto("https://corp.management-ui.turtle.aws.dev/role-mappings-view");
这一跳就不会再被 307 或 SSO 拦截，而是能拿到真正渲染好的数据。

抓取数据

从全局变量（window.__INITIAL_STATE__）

或拦截 XHR 返回

或根据 DOM 结构读取表格行

为什么必须这样？
浏览器环境看不到 HttpOnly：document.cookie 读不到，但网络层会自动带上。

Brazil 里没有直接读磁盘的能力：要先用 Python 把 Cookie 以结构化格式传进来。

一旦注入，后续所有 fetch/XHR 都照常走：无须再模拟登录、CSRF、重定向。

小结
Python → 读磁盘 Cookie → JSON

Brazil/JS → 加载 JSON → addCookies → goto

正常拿到前端数据 → 传回 Python/CLI → 渲染表格或导出

按这个思路走，就能在纯 Brazil 的流水线里成功带上那 13 条 Midway cookie，绕过 SSO 重定向，稳定抓到 role mappings。
















修改 test_utils.py 顶部为：

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../src/TurtleWebUICLI")))
from turtle_web_ui_cli.commands.utils import validate_midway_token


2. 本地用 Brazil 执行：

brazil-runtime-exec python3 -m pytest test/unit/commands/test_utils.py -v

你说得对，这个报错确实又回到了我们最早遇到的那个核心问题：

> ModuleNotFoundError: No module named 'turtle_web_ui_cli.commands'




---

从你刚刚发的整个 Brazil 输出判断：

🧠 问题本质是：

Brazil 构建环境中 没有正确设置 PYTHONPATH，导致它在执行 test/unit/commands/test_utils.py 时，无法找到 turtle_web_ui_cli.commands.utils 这个模块。


---

✅ 解法确认：

你当前项目结构是这样的（从你之前的图中看）：

turtle-cli-workspace/
  └── src/
        └── TurtleWebUICLI/
              ├── turtle_web_ui_cli/
              │     ├── commands/
              │     │     └── utils.py
              │     └── __init__.py
              └── test/
                    └── unit/
                          └── commands/
                                └── test_utils.py

你需要确保 Brazil 在运行 pytest 时，把 src/TurtleWebUICLI 加入 PYTHONPATH。


---

✅ Brazil 设置 PYTHONPATH 的两种方法：

✅ 方法 1：手动 Brazil Shell 测试验证

你可以运行：

brazil-build shell

然后在 shell 里执行：

export PYTHONPATH=$PWD/src/TurtleWebUICLI
pytest test/unit/commands/test_utils.py

如果这样能跑通，那说明根本问题只是 Brazil 没设置 PYTHONPATH。那我们就可以提交 CR 加上这个变量。


---

✅ 方法 2：提交 Brazil CR 让 test/build 自动设置 PYTHONPATH

修改 Brazil 的构建配置文件，一般在：

TurtleWebUICLI/brazil/config/common/configure

加入：

export PYTHONPATH=$BRAZIL_WORKSPACE/src/TurtleWebUICLI

或者如果是 Makefile 或 shell 脚本做 test entry point，也要加进去这个 export。


---

🧪 快速验证方式（推荐你马上试）：

cd /home/ambrowaw/workplace/turtle-cli-workspace/src/TurtleWebUICLI
export PYTHONPATH=$(pwd)
pytest test/unit/commands/test_utils.py

如果这能跑通，那我们可以立即 conclude：你的代码逻辑没问题，问题是 Brazil 没设 PYTHONPATH。


---

🧩 导入语句也确认下

你的 test 文件中应保持如下导入：

from turtle_web_ui_cli.commands.utils import validate_midway_token


---

✅ 总结你要做的事情：

步骤	操作

✅ 1	cd src/TurtleWebUICLI && export PYTHONPATH=$(pwd)
✅ 2	pytest test/unit/commands/test_utils.py 看能否跑通
✅ 3	如果跑通了，Brazil 中配置 PYTHONPATH
✅ 4	保留 from turtle_web_ui_cli.commands.utils import validate_midway_token


我可以帮你起草一个 Brazil CR 的 configure 环境变量 patch，如果你需要。你先跑通手动 export + pytest 看看是否能通。需要我写具体命令或者 Brazil patch 文件吗？


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../turtle_web_ui_cli")))

from commands.utils import validate_midway_token
你提到的 CR（Code Review）后无法调用 + dry run 失败，大概率是 测试脚本找不到模块路径，或者 Brazil 环境下 PYTHONPATH 没有配置好。

我们来一步步分析问题和解决方案：


---

✅ 一、问题本质

你的项目结构是这样的：

turtle-cli-workspace/
├── src/
│   └── TurtleWebUICLI/
│       └── commands/
│           └── utils.py
└── test/
    └── unit/
        └── commands/
            └── test_utils.py

但在 Brazil 或 dry run 运行时，Python 默认不会把 src/ 加入模块搜索路径，导致：

> ModuleNotFoundError: No module named 'TurtleWebUICLI'




---

✅ 二、解决方案

✅ 方法 1：Brazil-friendly 设置 PYTHONPATH

如果你是通过 Brazil 构建，Brazil 的 buildspec.yml 或打包脚本中必须加：

export PYTHONPATH=src

在 Brazil Dry Run 环境中，PYTHONPATH 不会自动加 src/，你得显式指定。


---

✅ 方法 2：项目根目录放 conftest.py（如果用 pytest）

创建这个空文件可帮助 pytest 正确识别模块结构：

turtle-cli-workspace/
└── test/
    └── conftest.py   ← 空文件


---

✅ 方法 3：使用 setup.py + editable install（高级）

如果你 Brazil 项目支持 setup.py 安装结构，你可以加：

# setup.py
from setuptools import setup, find_packages

setup(
    name="TurtleWebUICLI",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)

然后在 Brazil 构建中执行：

pip install -e .


---

✅ 三、补充建议（对 Brazil 特别重要）

建议	说明

✅ PYTHONPATH=src	最快最兼容 Brazil dry-run 的方法
✅ 不要用硬编码 sys.path	容易被 CR 拒掉
✅ 所有 import 用大写模块名	比如 from TurtleWebUICLI.commands import utils
✅ 测试文件中不要用绝对路径导入	Brazil 封装环境会失败



---

🛠 你现在应该做的检查

1. 进入 CLI 根目录，运行：

PYTHONPATH=src python -m unittest discover test


2. 如果成功了，就在 Brazil 构建或测试脚本中加：

export PYTHONPATH=src


3. 确保 test_utils.py 里面写的是：

from TurtleWebUICLI.commands.utils import validate_midway_token




---

需要我帮你写 Brazil build/test 配置文件（比如 buildspec.yml 或 test.sh）吗？只要你贴一下当前 Brazil 的脚本结构，我可以替你配置好。

这个 cookie 是本地 Midway 验证后的 cookie —— 存在 ~/.midway/cookie 文件中，包含完整认证状态（session、amzn_sso_token 等），是你本机登录 AWS 后 Midway SSO 认证完成的凭证。




---

🔑 关键理解：Midway Cookie ≠ 正常 Web 前端可访问 Cookie

这些 cookie 是 Midway 安全体系 在本地认证工具（比如你登录 AWS 内部门户，或者使用 midway-auth）时注入的；

它们大多数是：

HttpOnly

Secure

限定在 midway-auth.amazon.com 或 corp.management-ui.turtle.aws.dev 这样的域名下使用


所以它们不会出现在前端 JS 的 document.cookie 中

但会在发请求时自动附加到相应的域名中（前提是你在浏览器上下文中模拟得当）



---

🧨 你遇到的问题总结

你从 ~/.midway/cookie 成功拿到了全量的认证 cookie（✅ 没问题）

你用 Brazil / JS 环境跑脚本，但 只能看到 2 个 cookie，导致认证失败（因为缺少 session 等关键字段）

原因是：JS 永远无法看到 HttpOnly 的 cookie，即使你已经登录了

所以你尝试让 JS “读取 + 复用” 是从技术路径上不通的 ✅



---

✅ 正确做法：用 Playwright 注入 .midway/cookie 到浏览器上下文

只要你用 Python + Playwright，像这样：

context.add_cookies([
    {
        "name": "session",
        "value": "...",
        "domain": "corp.management-ui.turtle.aws.dev",
        "path": "/",
        "secure": True,
        "httpOnly": True,
        ...
    },
    ...
])

然后：

page.goto("https://corp.management-ui.turtle.aws.dev/role-mappings-view")

Midway 后端就会完全认出你已经登录过了，不再跳 307 到 SSO，而是直接返回数据。这时你可以从：

页面全局变量（如 window.__INITIAL_STATE__）

DOM 结构（.mapping-row）

或拦截 XHR 响应（/api/fetchRoleMappings）


获取你需要的内容，进而生成 CLI 输出（表格、JSON、CSV 等）。


---

✅ 结论：

你已经有了最核心的认证 cookie（从 .midway/cookie 读出来的）✅

不需要让 Brazil 或前端 JS 读取这些 cookie（它根本不能）❌

只需要在 Playwright / Selenium 等浏览器级别的上下文里 注入 cookie，就能让前端“像人一样”跑通 ✅

之后 CLI 抓取页面数据就完全可控了 ✅
当然可以，下面是你可以转发给另一个 AI 或同事的完整总结，语言简洁但包含所有技术要点：


---

✅ 项目目标：

从公司内部 Web UI（React 页面）中提取 role mappings 等数据，做一个 Python CLI 工具支持表格 / JSON / CSV 输出。


---

✅ 问题背景：

Web UI 前端依赖 Midway 登录认证，登录后的 session 信息保存在本地：~/.midway/cookie

这些 cookie 包含关键认证字段，如：session、amzn_sso_token，但大多为 HttpOnly

所以在前端环境（如 Brazil、Playwright 中的 JS）无法通过 JS 读取完整认证 cookie

尝试用 Brazil 直接发请求失败，因为认证信息不足



---

✅ 正确解决方案（已验证成功）：

1. 用 Python 读取 .midway/cookie（标准 Mozilla cookie 格式）

用 http.cookiejar.MozillaCookieJar 加载所有 cookie（包括 HttpOnly）



2. 用 Playwright 启动 headless 浏览器，并注入 cookie 到浏览器上下文

通过 context.add_cookies() 注入完整 cookie（包括 HttpOnly 和 Secure）

Playwright 浏览器将自动附带这些 cookie 发出认证请求



3. 用 page.goto(...) 打开前端页面

比如：https://corp.management-ui.turtle.aws.dev/role-mappings-view



4. 等待前端完成加载，获取数据

方法一：从全局变量读取（如 window.__INITIAL_STATE__）

方法二：等待 .mapping-row 等 DOM 元素出现并解析

方法三：监听并提取 XHR 请求（如 /api/fetchRoleMappings）的 JSON 响应



5. 将数据传回 CLI，支持 --format table/json/csv 输出




---

✅ 为什么方案有效：

避免用 JS 获取 cookie，绕过 HttpOnly 限制

不需要模拟复杂的登录流程、SSO 跳转、CSRF token 等

浏览器自动完成所有认证逻辑

CLI 逻辑只需处理数据展示即可



---

如需参考实现代码，可包含：

Cookie 解析模块

Playwright 页面访问与数据抽取模块

CLI 输出模块（使用 argparse + rich/tabulate/csv/json）


是否需要样例代码，也可以提供。


