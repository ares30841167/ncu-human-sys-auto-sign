import time
from apscheduler.schedulers.background import BackgroundScheduler
from ncu_hsys.sign_bot import do_sign_flow


# 人事系統簽到退相關參數 (PORTAL_TOKEN, PARTTIME_USUALLY_ID)
SIGN_ARGS = (
    "20240221101901W7T....", 123456)

if __name__ == "__main__":
    # 背景執行排程器
    scheduler = BackgroundScheduler()

    # 新增簽到退排程工作
    scheduler.add_job(func=do_sign_flow, args=SIGN_ARGS, trigger="cron", day="17-25",
                      hour="13", minute="0", replace_existing=True, id="sign_in_task")
    scheduler.add_job(func=do_sign_flow, args=SIGN_ARGS, trigger="cron", day="17-25",
                      hour="16", minute="10", replace_existing=True, id="sign_out_task")

    # 開始簽到退排程作業並印出排程狀態訊息供確認
    scheduler.start()
    scheduler.print_jobs()

    try:
        while (True):
            # 空迴圈保持主程式運行
            # 未來擴充 TODO
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Ctrl-C 結束程式 或 程式終止時印出提示
        print("\n終止簽到退排程作業")
