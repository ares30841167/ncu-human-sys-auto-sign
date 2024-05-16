import requests
from ..constants import ACCEPT_LANGUAGE, BROWSER_USER_AGENT, PORTAL_COOKIE_DOMAIN


def init_browser(portal_toekn: str) -> requests.Session:
    # 初始化 Session
    browser = requests.Session()
    # 將 PORTAL_TOKEN 設定為 cookie: portal
    browser.cookies.set("portal", portal_toekn, domain=PORTAL_COOKIE_DOMAIN)
    # 設定模擬瀏覽器的 User-Agent Header
    browser.headers.update(
        {"User-Agent": BROWSER_USER_AGENT, "Accept-Language": ACCEPT_LANGUAGE})

    return browser
