import os
import re
import logging
import requests
from lxml import etree
from dotenv import load_dotenv
from notification.notifier import Notifier
from .constants import NCU_PORTAL_URL, HUMAN_SYS_URL, MENU_SELECT, \
    LOGIN_PAGE_XPATH, SIGNIN_PAGE_XPATH, BROWSER_USER_AGENT, PORTAL_COOKIE_DOMAIN


def init_logger():
    FORMAT = '%(asctime)s %(filename)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)


def init_env() -> None:
    # 讀取 .env 檔案
    load_dotenv()

    # 檢查 PORTAL_TOKEN 是否存在 .env 內
    if ("PORTAL_TOKEN" not in os.environ):
        raise Exception("未設定環境變數 PORTAL_TOEKN")

    # 檢查 PARTTIME_USUALLY_ID 是否存在 .env 內
    if ("PARTTIME_USUALLY_ID" not in os.environ):
        raise Exception("未設定環境變數 PARTTIME_USUALLY_ID")

    # 檢查 PORTAL_TOKEN 是否為空
    if (os.environ.get("PORTAL_TOKEN") == ""):
        raise Exception("PORTAL_TOEKN不得為空")

    # 檢查 PARTTIME_USUALLY_ID 是否為空
    if (os.environ.get("PARTTIME_USUALLY_ID") == ""):
        raise Exception("PARTTIME_USUALLY_ID不得為空")

    # 檢查 PARTTIME_USUALLY_ID 是否為數字
    try:
        int(os.environ.get("PARTTIME_USUALLY_ID"))
    except:
        raise Exception("PARTTIME_USUALLY_ID無法正確轉換為數字")


def check_type(portal_token: str, parttime_usually_id: int) -> None:
    # 檢查 portal_token 是否為 str
    if (not isinstance(portal_token, str)):
        raise TypeError("portal_token 並非字串")

    # 檢查 parttime_usually_id 是否為 int
    if (not isinstance(parttime_usually_id, int)):
        raise TypeError("parttime_usually_id 並非整數")


def init_browser(portal_toekn: str) -> requests.Session:
    # 初始化 Session
    browser = requests.Session()
    # 將 PORTAL_TOKEN 設定為 cookie: portal
    browser.cookies.set("portal", portal_toekn, domain=PORTAL_COOKIE_DOMAIN)
    # 設定模擬瀏覽器的 User-Agent Header
    browser.headers.update({"User-Agent": BROWSER_USER_AGENT})

    return browser


def login_ncu_portal(browser: requests.Session) -> None:
    # 進到 Portal 登入畫面
    res = browser.get(NCU_PORTAL_URL.LOGIN)

    # 解析回應
    html = etree.HTML(res.text)

    # 在頁面中尋找對應的表單輸入內容
    # 若正確使用有效的 PORTAL_TOKEN 會在頁面上自動帶入所有輸入內容
    csrf = html.xpath(LOGIN_PAGE_XPATH.CSRF)[0]
    login_name = html.xpath(LOGIN_PAGE_XPATH.LOGIN_NAME)[0]
    username = html.xpath(LOGIN_PAGE_XPATH.USERNAME)[0]
    remember_as = html.xpath(LOGIN_PAGE_XPATH.REMEMBER_AS)[0]

    # 製作登入請求
    payload = {
        "_csrf": csrf,
        "login-name": login_name,
        "username": username,
        "remember-as": remember_as
    }

    # 對登入頁面用 POST 帶登入請求進行登入
    res = browser.post(NCU_PORTAL_URL.LOGIN, data=payload)


def fetch_human_sys_redirect_url(browser: requests.Session) -> str:
    # 獲取 Portal 選單 API 的回應
    res = browser.get(NCU_PORTAL_URL.MENU_BACKEND)

    # 嘗試將回應使用 JSON 格式解析
    menu = {}
    try:
        menu = res.json()
    except:
        raise Exception("無法取得NCU Portal功能選單，請嘗試更新PORTAL_TOKEN")

    # 提取人事系統的重導向 URL，此 URL 後面會自帶 Token
    human_sys_redirect_url = ""
    try:
        # 透過 JSON 內的相對位置提取對應的 URL
        menu_entries = menu["menuEntries"]
        student_service_submenu = menu_entries[MENU_SELECT.STUDENT_SERVICE]["submenu"]
        student_assistance_service_submenu = student_service_submenu[
            MENU_SELECT.STUDENT_ASSISTANCE_SERVICE]["submenu"]
        human_sys_redirect_url = student_assistance_service_submenu[MENU_SELECT.HUMAN_SYS]["url"]
    except:
        raise Exception("從NCU Portal選單獲取人事系統重導向URL失敗")

    # 檢查提取的 URL 是否為空值
    if (human_sys_redirect_url == ""):
        raise Exception("人事系統重導向URL為空")

    return human_sys_redirect_url


def login_human_sys(browser: requests.Session, human_sys_redirect_url: str) -> None:
    # 使用帶有 Token 的 URL 重新導向到人事系統
    browser.get(NCU_PORTAL_URL.BASE + human_sys_redirect_url)


def gen_signin_payload(browser: requests.Session, parttime_usually_id: int) -> dict:
    # 檢查 cookie: locale 是否存在，正確登入人事系統此 Cookie 應該要存在
    try:
        browser.cookies["locale"]
    except KeyError:
        raise Exception("未正常登入人事系統(請不要在執行的過程中登入或瀏覽操作NCU Portal)")

    # 使用 PARTTIME_USUALLY_ID 進到目標簽到頁面
    res = browser.get(HUMAN_SYS_URL.CREATE_SIGNIN, params={
                      "ParttimeUsuallyId": parttime_usually_id})

    # 解析頁面
    html = etree.HTML(res.text)

    # 從頁面提取目前簽到的紀錄 ID
    # 若為簽到狀態為空值，若為簽退狀態則為上次簽到的紀錄 ID
    id_no = html.xpath(SIGNIN_PAGE_XPATH.ID_NO)[0]

    # 從頁面中的 Javascript 腳本提取用於呼叫簽到 API 的 Token
    core_script = html.xpath(SIGNIN_PAGE_XPATH.CORE_SCRIPT)[0]
    token = re.findall("_token : \"(\w*)\"", core_script)[0]

    # 檢查提取的 Token 是否為空值
    if (token == ""):
        raise Exception("無法從人事系統中的 Core Script 找到 Token")

    # 製作簽到請求
    payload = {
        "functionName": "doSign",
        "idNo": id_no,
        "ParttimeUsuallyId": parttime_usually_id,
        "AttendWork": "工讀生",
        "_token": token
    }

    return payload


def do_sign_act(browser: requests.Session, payload: dict, notify: bool = False) -> None:
    # 對簽到 API 用 POST 帶簽到請求進行簽到
    res = browser.post(HUMAN_SYS_URL.SIGNIN_BACKEND, data=payload)

    # 若啟用通知功能，則初始化通知通道
    notifier = Notifier() if notify else None

    # 紀錄結果
    try:
        # 判斷簽到 API 是否回傳簽到成功之提示並印出本地結果提示
        if (res.json()["isOK"] == "Y"):
            msg = "簽到成功" if payload["idNo"] == "" else "簽退成功"
            logging.info(msg)
            if (notify):
                notifier.notify(msg)
        else:
            msg = "簽到退失敗，後端回應錯誤: {}".format(res.json())
            logging.info(msg)
            if (notify):
                notifier.notify(msg)
    except:
        raise Exception("簽到退失敗(無isOK欄位)，後端回應錯誤: {}".format(res.json()))


def do_sign_flow(portal_token: str, parttime_usually_id: int, notify: bool = True) -> None:
    # 檢查傳入的變數型別
    check_type(portal_token, parttime_usually_id)

    # 初始化 Requests Session
    browser = init_browser(portal_token)

    # 登入 NCU Portal
    login_ncu_portal(browser)

    # 重新導向到人事系統並登入
    human_sys_redirect_url = fetch_human_sys_redirect_url(browser)
    login_human_sys(browser, human_sys_redirect_url)

    # 產生簽到請求並進行簽到
    signin_payload = gen_signin_payload(browser, parttime_usually_id)
    do_sign_act(browser, signin_payload, notify)


if __name__ == "__main__":
    # 初始化 Logger
    init_logger()

    # 初始化環境變數
    init_env()

    # 從環境變數提取 portal_token 與 parttime_usually_id
    # parttime_usually_id 的型態檢查在 init_env 有做過
    portal_token = os.environ.get("PORTAL_TOKEN")
    parttime_usually_id = int(os.environ.get("PARTTIME_USUALLY_ID"))

    # 執行簽到退流程
    do_sign_flow(portal_token, parttime_usually_id, False)
