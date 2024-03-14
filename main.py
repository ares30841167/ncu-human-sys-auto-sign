import os
import time
import logging
import argparse
from utils.dot_env import init_env
from utils.logger import init_logger
from ncu_hsys.sign_bot import do_sign_flow
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from listener.apscheduler import APSchedulerEventHandler
from apscheduler.schedulers.background import BackgroundScheduler

# 解析參數


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='啟用 debug 日誌輸出模式',
                        required=False)

    return parser.parse_args()


if __name__ == "__main__":
    # 解析參數
    args = parse_args()

    # 初始化 Logger
    init_logger(args.verbose)

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

    # 創建任務事件監聽器
    event_handler = APSchedulerEventHandler(scheduler)

    # 註冊任務事件，讓事件呼叫任務事件監聽器
    scheduler.add_listener(
        event_handler.success_event_handler, EVENT_JOB_EXECUTED)
    scheduler.add_listener(
        event_handler.exception_event_handler, EVENT_JOB_ERROR)

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
