from pathlib import Path
import json
from http.cookiejar import MozillaCookieJar
from playwright.sync_api import sync_playwright

def load_mozilla_cookies(path):
    jar = MozillaCookieJar(path)
    jar.load(ignore_discard=True, ignore_expires=True)
    cookies = []
    for c in jar:
        # Playwright 要求的字段
        cookies.append({
            "name":     c.name,
            "value":    c.value,
            "domain":   c.domain,
            "path":     c.path,
            "expires":  c.expires or -1,
            "httpOnly": c._rest.get("HttpOnly", False),
            "secure":   c.secure,
            "sameSite": "Lax",          # 或者 "None"/"Strict"，根据你的情况调
        })
    return cookies

def fetch_role_mappings():
    cookie_file = Path.home() / ".midway" / "cookie"
    cookies = load_mozilla_cookies(str(cookie_file))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # 把 Midway SSO 的 Cookie 注入到浏览器上下文
        context.add_cookies(cookies)

        page = context.new_page()
        # 访问前端路由，前端 JS 会自动带上 Cookie 去拿数据
        page.goto("https://corp.management-ui.turtle.aws.dev/role-mappings-view")

        # 等待数据表渲染完成（根据你页面上的 CSS 选择器调整）
        page.wait_for_selector(".mapping-row")

        # 方法 A：直接从全局变量里取（如果前端把请求结果挂到 window）
        data = page.evaluate("() => window.__INITIAL_STATE__.roleMappings")

        # 方法 B：拦截真实的 XHR 返回
        # mappings = []
        # def on_response(resp):
        #     if "/api/admin/v2/roleMappings/search" in resp.url:
        #         mappings.append(resp.json())
        # page.on("response", on_response)
        # page.reload()          # 或者直接在 goto 后等待

        browser.close()
        return data

if __name__ == "__main__":
    mappings = fetch_role_mappings()
    print(json.dumps(mappings, indent=2))
