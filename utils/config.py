import os
from utils.cron import validate_cron_expression, validate_cron_jobs_scheduling_config


def validate_config():
    # 從環境變數取得排程時間相關設定變數
    signing_day = os.environ.get("SIGNING_DAY")
    sign_in_hour = os.environ.get("SIGN_IN_HOUR")
    sign_in_minutes = os.environ.get("SIGN_IN_MINUTES")
    sign_out_hour = os.environ.get("SIGN_OUT_HOUR")
    sign_out_minutes = os.environ.get("SIGN_OUT_MINUTES")

    # 將排程時間變數組合成 cron 表達式字串
    sign_in_job_cron = f"{sign_in_minutes} {sign_in_hour} {signing_day} * *"
    sign_out_job_cron = f"{sign_out_minutes} {sign_out_hour} {signing_day} * *"

    # 驗證 cron 表達式的正確性
    if (not validate_cron_expression(sign_in_job_cron)):
        raise Exception("簽到排程 cron 表達式格式設定錯誤")
    if (not validate_cron_expression(sign_out_job_cron)):
        raise Exception("簽退排程 cron 表達式格式設定錯誤")

    # 檢查簽到退排程任務的正確性
    validate_cron_jobs_scheduling_config(sign_in_job_cron, sign_out_job_cron)
