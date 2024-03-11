import os
import time
import logging
from utils.dot_env import init_env
from utils.logger import init_logger
from ncu_hsys.sign_bot import do_sign_flow
from apscheduler.schedulers.background import BackgroundScheduler


if __name__ == "__main__":
    # 初始化 Logger
    init_logger()

    # 初始化環境變數
    init_env()

    # 人事系統簽到退相關參數 (PORTAL_TOKEN, PARTTIME_USUALLY_ID)
    SIGN_ARGS = (
        os.environ.get("PORTAL_TOKEN"), int(os.environ.get("PARTTIME_USUALLY_ID")))

    # 背景執行排程器
    scheduler = BackgroundScheduler()

    # 新增簽到退排程工作
    scheduler.add_job(func=do_sign_flow, args=SIGN_ARGS, trigger="cron", day=os.environ.get("SIGN_IN_DAY"),
                      hour=os.environ.get("SIGN_IN_HOUR"), minute=os.environ.get("SIGN_IN_MINUTES"),
                      replace_existing=True, id="sign_in_task")
    scheduler.add_job(func=do_sign_flow, args=SIGN_ARGS, trigger="cron", day=os.environ.get("SIGN_OUT_DAY"),
                      hour=os.environ.get("SIGN_OUT_HOUR"), minute=os.environ.get("SIGN_OUT_MINUTES"),
                      replace_existing=True, id="sign_out_task")

    # 開始簽到退排程作業並印出排程狀態訊息供確認
    scheduler.start()

    try:
        while (True):
            # 空迴圈保持主程式運行
            # 未來擴充 TODO
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Ctrl-C 結束程式 或 程式終止時紀錄事件
        logging.info("終止簽到退排程作業")
