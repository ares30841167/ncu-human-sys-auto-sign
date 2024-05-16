import logging
import os
from lxml import etree
from ncu_hsys.constants import NCU_PORTAL_URL, LOGIN_PAGE_XPATH
from ncu_hsys.utils.browser import init_browser


def verify_ncu_portal_token() -> None:
    # 從環境變數取得 PORTAL_TOKEN
    portal_token = os.environ.get("PORTAL_TOKEN")

    # 初始化 Requests Session
    browser = init_browser(portal_token)

    # 進到 Portal 登入畫面
    res = browser.get(NCU_PORTAL_URL.LOGIN)

    # 解析回應
    html = etree.HTML(res.text)

    # 在頁面中尋找 Token 有效期限
    # 若正確使用有效的 PORTAL_TOKEN 會在頁面上找到「記住我」登入剩餘有效時間
    try:
        remaing_day_msg = html.xpath(LOGIN_PAGE_XPATH.REMAING_DAY_MSG)[0]
        logging.info(remaing_day_msg)
    except IndexError:
        raise Exception("PORTAL_TOKEN無效，請重新檢查其登入狀態有效性")
