import os
import re
import requests
from lxml import etree
from datetime import datetime
from dotenv import load_dotenv
from constants import NCU_PORTAL_URL, HUMAN_SYS_URL, MENU_SELECT, \
    LOGIN_PAGE_XPATH, SIGNIN_PAGE_XPATH, BROWSER_USER_AGENT


def init_env() -> None:
    load_dotenv()

    if ("PORTAL_TOKEN" not in os.environ):
        raise Exception("未設定環境變數 PORTAL_TOEKN")

    if ("PARTTIME_USUALLY_ID" not in os.environ):
        raise Exception("未設定環境變數 PARTTIME_USUALLY_ID")

    if (os.environ.get("PORTAL_TOKEN") == ""):
        raise Exception("PORTAL_TOEKN不得為空")

    if (os.environ.get("PARTTIME_USUALLY_ID") == ""):
        raise Exception("PARTTIME_USUALLY_ID不得為空")

    try:
        int(os.environ.get("PARTTIME_USUALLY_ID"))
    except:
        raise Exception("PARTTIME_USUALLY_ID無法正確轉換為數字")


def init_browser() -> requests.Session:
    browser = requests.Session()
    browser.cookies.set("portal", os.environ.get("PORTAL_TOKEN"))
    browser.headers.update({"User-Agent": BROWSER_USER_AGENT})

    return browser


def login_ncu_portal(browser: requests.Session) -> None:
    res = browser.get(NCU_PORTAL_URL.LOGIN)

    html = etree.HTML(res.text)

    csrf = html.xpath(LOGIN_PAGE_XPATH.CSRF)[0]
    login_name = html.xpath(LOGIN_PAGE_XPATH.LOGIN_NAME)[0]
    username = html.xpath(LOGIN_PAGE_XPATH.USERNAME)[0]
    remember_as = html.xpath(LOGIN_PAGE_XPATH.REMEMBER_AS)[0]

    payload = {
        "_csrf": csrf,
        "login-name": login_name,
        "username": username,
        "remember-as": remember_as
    }

    res = browser.post(NCU_PORTAL_URL.LOGIN, data=payload)


def fetch_human_sys_redirect_url(browser: requests.Session) -> str:
    res = browser.get(NCU_PORTAL_URL.MENU_BACKEND)

    menu = {}
    try:
        menu = res.json()
    except:
        raise Exception("無法取得NCU Portal功能選單，請嘗試更新PORTAL_TOKEN")

    human_sys_redirect_url = ""
    try:
        menu_entries = menu["menuEntries"]
        student_service_submenu = menu_entries[MENU_SELECT.STUDENT_SERVICE]["submenu"]
        student_assistance_service_submenu = student_service_submenu[
            MENU_SELECT.STUDENT_ASSISTANCE_SERVICE]["submenu"]
        human_sys_redirect_url = student_assistance_service_submenu[MENU_SELECT.HUMAN_SYS]["url"]
    except:
        raise Exception("從NCU Portal選單獲取人事系統重導向URL失敗")

    if (human_sys_redirect_url == ""):
        raise Exception("人事系統重導向URL為空")

    return human_sys_redirect_url


def login_human_sys(browser: requests.Session, human_sys_redirect_url: str) -> None:
    browser.get(NCU_PORTAL_URL.BASE + human_sys_redirect_url)


def gen_signin_payload(browser: requests.Session) -> dict:
    try:
        browser.cookies["locale"]
    except KeyError:
        raise Exception("未正常登入人事系統(請不要在執行的過程中登入或瀏覽操作NCU Portal)")

    PARTTIME_USUALLY_ID = 0
    try:
        PARTTIME_USUALLY_ID = int(os.environ.get("PARTTIME_USUALLY_ID"))
    except:
        raise Exception("PARTTIME_USUALLY_ID無法正確轉換為數字")

    res = browser.get(HUMAN_SYS_URL.CREATE_SIGNIN, params={
                      "ParttimeUsuallyId": PARTTIME_USUALLY_ID})

    html = etree.HTML(res.text)

    id_no = html.xpath(SIGNIN_PAGE_XPATH.ID_NO)[0]

    core_script = html.xpath(SIGNIN_PAGE_XPATH.CORE_SCRIPT)[0]
    token = re.findall("_token : \"(\w*)\"", core_script)[0]

    if (token == ""):
        raise Exception("無法從人事系統中的 Core Script 找到 Token")

    payload = {
        "functionName": "doSign",
        "idNo": id_no,
        "ParttimeUsuallyId": PARTTIME_USUALLY_ID,
        "AttendWork": "工讀生",
        "_token": token
    }

    return payload


def do_sign_act(browser: requests.Session, payload: dict) -> None:
    res = browser.post(HUMAN_SYS_URL.SIGNIN_BACKEND, data=payload)

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[{}]".format(timestamp), end=" ")

        if (res.json()["isOK"] == "Y"):
            print("簽到成功" if payload["id_no"] == "" else "簽退成功")
        else:
            print("簽到退失敗，後端回應錯誤: {}".format(res.json()))
    except:
        raise Exception("簽到退失敗(無isOK欄位)，後端回應錯誤: {}".format(res.json()))


if __name__ == "__main__":
    init_env()

    browser = init_browser()

    login_ncu_portal(browser)

    human_sys_redirect_url = fetch_human_sys_redirect_url(browser)
    login_human_sys(browser, human_sys_redirect_url)

    signin_payload = gen_signin_payload(browser)
    do_sign_act(browser, signin_payload)
