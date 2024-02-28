import os
import re
import requests
from lxml import etree
from datetime import datetime
from dotenv import load_dotenv
from constants import NCU_PORTAL_URL, HUMAN_SYS_URL, MENU_SELECT, \
    LOGIN_PAGE_XPATH, SIGNIN_PAGE_XPATH, BROWSER_USER_AGENT, PORTAL_COOKIE_DOMAIN


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


def init_browser() -> requests.Session:
    # 初始化 Session
    browser = requests.Session()
    # 將 PORTAL_TOKEN 設定為 cookie: portal
    browser.cookies.set("portal", os.environ.get(
        "PORTAL_TOKEN"), domain=PORTAL_COOKIE_DOMAIN)
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


def gen_signin_payload(browser: requests.Session) -> dict:
    # 檢查 cookie: locale 是否存在，正確登入人事系統此 Cookie 應該要存在
    try:
        browser.cookies["locale"]
    except KeyError:
        raise Exception("未正常登入人事系統(請不要在執行的過程中登入或瀏覽操作NCU Portal)")

    # 嘗試將 PARTTIME_USUALLY_ID 轉換成 int
    PARTTIME_USUALLY_ID = 0
    try:
        PARTTIME_USUALLY_ID = int(os.environ.get("PARTTIME_USUALLY_ID"))
    except:
        raise Exception("PARTTIME_USUALLY_ID無法正確轉換為數字")

    # 使用 PARTTIME_USUALLY_ID 進到目標簽到頁面
    res = browser.get(HUMAN_SYS_URL.CREATE_SIGNIN, params={
                      "ParttimeUsuallyId": PARTTIME_USUALLY_ID})

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
        "ParttimeUsuallyId": PARTTIME_USUALLY_ID,
        "AttendWork": "工讀生",
        "_token": token
    }

    return payload


def do_sign_act(browser: requests.Session, payload: dict) -> None:
    # 對簽到 API 用 POST 帶簽到請求進行簽到
    res = browser.post(HUMAN_SYS_URL.SIGNIN_BACKEND, data=payload)

    # 印出結果提示
    try:
        # 取得現在時間戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[{}]".format(timestamp), end=" ")

        # 判斷簽到 API 是否回傳簽到成功之提示並印出本地結果提示
        if (res.json()["isOK"] == "Y"):
            print("簽到成功" if payload["idNo"] == "" else "簽退成功")
        else:
            print("簽到退失敗，後端回應錯誤: {}".format(res.json()))
    except:
        raise Exception("簽到退失敗(無isOK欄位)，後端回應錯誤: {}".format(res.json()))


if __name__ == "__main__":
    # 初始化環境變數
    init_env()

    # 初始化 Requests Session
    browser = init_browser()

    # 登入 NCU Portal
    login_ncu_portal(browser)

    # 重新導向到人事系統並登入
    human_sys_redirect_url = fetch_human_sys_redirect_url(browser)
    login_human_sys(browser, human_sys_redirect_url)

    # 產生簽到請求並進行簽到
    signin_payload = gen_signin_payload(browser)
    do_sign_act(browser, signin_payload)
