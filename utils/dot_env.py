import os
from dotenv import load_dotenv


def init_env() -> None:
    # 讀取 .env 檔案
    load_dotenv()

    # 檢查 PORTAL_TOKEN 是否存在 .env 內
    if ("PORTAL_TOKEN" not in os.environ):
        raise Exception("未設定環境變數 PORTAL_TOEKN")

    # 檢查 PARTTIME_USUALLY_ID 是否存在 .env 內
    if ("PARTTIME_USUALLY_ID" not in os.environ):
        raise Exception("未設定環境變數 PARTTIME_USUALLY_ID")

    # 檢查 SIGNING_DAY 是否存在 .env 內
    if ("SIGNING_DAY" not in os.environ):
        raise Exception("未設定環境變數 SIGNING_DAY")

    # 檢查 SIGN_IN_HOUR 是否存在 .env 內
    if ("SIGN_IN_HOUR" not in os.environ):
        raise Exception("未設定環境變數 SIGN_IN_HOUR")

    # 檢查 SIGN_IN_MINUTES 是否存在 .env 內
    if ("SIGN_IN_MINUTES" not in os.environ):
        raise Exception("未設定環境變數 SIGN_IN_MINUTES")

    # 檢查 SIGN_OUT_HOUR 是否存在 .env 內
    if ("SIGN_OUT_HOUR" not in os.environ):
        raise Exception("未設定環境變數 SIGN_OUT_HOUR")

    # 檢查 SIGN_OUT_MINUTES 是否存在 .env 內
    if ("SIGN_OUT_MINUTES" not in os.environ):
        raise Exception("未設定環境變數 SIGN_OUT_MINUTES")

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

    # 檢查 SIGNING_DAY 是否為空
    if (os.environ.get("SIGNING_DAY") == ""):
        raise Exception("SIGNING_DAY不得為空")

    # 檢查 SIGN_IN_HOUR 是否為空
    if (os.environ.get("SIGN_IN_HOUR") == ""):
        raise Exception("SIGN_IN_HOUR不得為空")

    # 檢查 SIGN_IN_MINUTES 是否為空
    if (os.environ.get("SIGN_IN_MINUTES") == ""):
        raise Exception("SIGN_IN_MINUTES不得為空")

    # 檢查 SIGN_OUT_HOUR 是否為空
    if (os.environ.get("SIGN_OUT_HOUR") == ""):
        raise Exception("SIGN_OUT_HOUR不得為空")

    # 檢查 SIGN_OUT_MINUTES 是否為空
    if (os.environ.get("SIGN_OUT_MINUTES") == ""):
        raise Exception("SIGN_OUT_MINUTES不得為空")
