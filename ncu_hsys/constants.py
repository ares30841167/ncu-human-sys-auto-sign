class NCU_PORTAL_URL(enumerate):
    BASE = "https://portal.ncu.edu.tw"
    LOGIN = BASE + "/login"
    MENU_BACKEND = BASE + "/backends/menu"


class HUMAN_SYS_URL(enumerate):
    BASE = "https://cis.ncu.edu.tw/HumanSys"
    CREATE_SIGNIN = BASE + "/student/stdSignIn/create"
    SIGNIN_BACKEND = BASE + "/student/stdSignIn_detail"


class MENU_SELECT(enumerate):
    STUDENT_SERVICE = 1
    STUDENT_SERVICE = 1
    STUDENT_ASSISTANCE_SERVICE = 3
    HUMAN_SYS = 5


class LOGIN_PAGE_XPATH(enumerate):
    CSRF = "/html/body/section/div/div/div[1]/div/div/form/input/@value"
    LOGIN_NAME = "//*[@id=\"inputAccount\"]/@value"
    USERNAME = "/html/body/section/div/div/div[1]/div/div/form/fieldset/div[1]/input[2]/@value"
    REMEMBER_AS = "/html/body/section/div/div/div[1]/div/div/form/fieldset/div[1]/input[3]/@value"
    REMAING_DAY_MSG = "/html/body/section/div/div/div[1]/div/div/form/fieldset/div[1]/ul/li[1]/text()"


class SIGNIN_PAGE_XPATH(enumerate):
    ID_NO = "//*[@id=\"idNo\"]/@value"
    CORE_SCRIPT = "/html/body/div[4]/div/script/text()"


ACCEPT_LANGUAGE = "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4"
BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
PORTAL_COOKIE_DOMAIN = "portal.ncu.edu.tw"
