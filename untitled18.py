✅ 背景：浏览器只发送匹配的 Cookie（不是数量越多越好）
浏览器不会把你本地的所有 cookie 都发给服务器，它只会发送满足以下三重匹配条件的 cookie：

domain 匹配（必须是当前请求域名或其父域）

path 匹配（当前请求的路径必须在 cookie 设置的 path 下）

secure / httpOnly / sameSite 等限制不被触发

而 Python 的 cookiejar 默认会把全部 cookie 都读出来。所以你看到 Python 读了 4 个，而实际 Web 请求只带了 2 个，这种不对称是正常的。

🔍 你该如何检查 cookie 是否被正确发送？
推荐方式：用 cookiejar 自动匹配、生成 cookie header
python
Copy
Edit
import http.cookiejar
import urllib.request

jar = http.cookiejar.MozillaCookieJar("~/.midway/cookie")
jar.load(ignore_discard=True, ignore_expires=True)

req = urllib.request.Request("https://corp.management-ui.turtle.aws.dev/api/fetchRoleMappings")
jar.add_cookie_header(req)

# 获取最终要发送的 Cookie 头
cookie_header = req.get_header("Cookie")
print("Cookie being sent:", cookie_header)
这样生成的 cookie_header 会严格模拟浏览器行为——只发给当前 URL 会用到的 cookie。

🧨 常见失败原因排查
问题	说明
Cookie domain 不匹配	你访问的是 corp.management-ui.turtle.aws.dev，但 cookie 是 midway-auth.amazon.com 域的，浏览器不会发送
Cookie 缺失关键字段	比如少了 amzn_sso_rfp=... 或 session=...，就会触发重定向到 SSO
Cookie 是加密生成的临时票据	有效期很短（几分钟），你手动复制过来的可能已经失效
你的 CLI 只传了部分 cookie	手动拼接 Cookie: 时遗漏了关键字段，建议用 jar.add_cookie_header() 自动生成
用的是错误的接口	前端可能用的是带 SigV4 的 AWS API（非 cookie 驱动），而你 CLI 用的是不同接口或未签名请求

✅ 建议你采取的行动
用 add_cookie_header 自动挑 cookie，而不是你手动 join 四个。

打印出你实际请求的：

URL

Method

Headers，特别是 Cookie

对比 DevTools 中那条 fetch 请求的 cookie 行，确保：

必要 cookie 没漏；

不多发（比如发了 Path=/login 的 cookie 会触发问题）；

如果还是 307 or 401，把后端返回的 JSON 打印出来，它通常会说：

json
Copy
Edit
{
  "status": "error",
  "message": "Unauthenticated",
  "desc": "Missing session cookie"
}
🛠 如果你需要，我可以帮你写一个自动打印：
bash
Copy
Edit
✅ 正确加载 cookie
✅ 输出将被发送的 Cookie 行
✅ 打印完整请求信息和响应 JSON
你只需要告诉我你当前使用的请求 URL 和请求方式（GET/POST 以及 headers），我就可以生成这个完整调试脚本。是否需要我帮你生成？
