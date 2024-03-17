import logging
from typing import Generator
from datetime import datetime, timedelta
from croniter import CroniterBadCronError, croniter


def get_days_in_current_month() -> int:
    # 取得目前時間並賦予給 datetime 指針
    datetime_ptr = datetime.now()

    # 取得下一個月一號的 datetime 物件
    next_month = 1 if datetime_ptr.month + 1 > 12 else datetime_ptr.month + 1
    first_day_in_next_month = datetime_ptr.replace(month=next_month, day=1)

    # 使用下個月第一天減去一天來取得這個月的最後一天
    days_in_current_month = first_day_in_next_month - timedelta(days=1)

    return days_in_current_month.day


def get_minutes_diff_between(sign_in_job_cron: str, sign_out_job_cron: str) -> Generator:
    # 取得此月份的天數
    days_in_current_month = get_days_in_current_month()

    # 對這個月所有的天數做迭代
    for day in range(1, days_in_current_month + 1):
        # 將 datetime 指針調整為當前迭代到的天數
        datetime_ptr = datetime.now().replace(day=day, hour=0, minute=0, second=0)

        # 以此 datetime 指針為時間點計算下一次的排程執行時間為何
        next_sign_in_job = croniter(
            sign_in_job_cron, datetime_ptr).get_next(datetime)
        next_sing_out_job = croniter(
            sign_out_job_cron, datetime_ptr).get_next(datetime)

        # 計算此迭代之簽到退排程任務之間的分鐘數差距
        time_diff_in_minutes = abs(
            (next_sing_out_job - next_sign_in_job).total_seconds() // 60)

        yield int(time_diff_in_minutes)


def get_min_minutes_diff_between(sign_in_job_cron: str, sign_out_job_cron: str) -> int:
    # 紀錄這個月內所有排程任務之間最小的分鐘差距
    min_minutes_diff = float("inf")

    # 對這個月所有的天數做迭代
    for minutes_diff in get_minutes_diff_between(sign_in_job_cron, sign_out_job_cron):
        # 若小於過往最小值，則更新最小值為當前分鐘數差距
        min_minutes_diff = min(min_minutes_diff, minutes_diff)

    return int(min_minutes_diff)


def get_max_hours_diff_between(sign_in_job_cron: str, sign_out_job_cron: str) -> int:
    # 紀錄這個月內所有排程任務之間最小的分鐘差距
    max_hours_diff = 0

    # 對這個月所有的天數做迭代
    for minutes_diff in get_minutes_diff_between(sign_in_job_cron, sign_out_job_cron):
        # 若大於過往最大值，則更新最大值為當前小時數差距
        max_hours_diff = max(max_hours_diff, (minutes_diff // 60))

    return max_hours_diff


def validate_cron_expression(cron_expr: str) -> bool:
    # 使用 croniter 套件驗證 cron 表達式是否正確
    try:
        croniter(cron_expr)
        return True
    except CroniterBadCronError:
        return False


def validate_cron_jobs_overlap(sign_in_job_cron: str, sign_out_job_cron: str) -> None:
    # 取得這個月內所有排程任務之間最小的分鐘差距
    min_minute_diff = get_min_minutes_diff_between(
        sign_in_job_cron, sign_out_job_cron)

    # 拋出錯誤若兩排程任務間差距小於等於五分鐘 (重試機制所限制)
    if (min_minute_diff <= 5):
        raise Exception("簽到退排程任務間間隔需大於五分鐘以上，請調整 cron 表達式")


def validate_cron_jobs_correctness(sign_in_job_cron: str, sign_out_job_cron: str) -> None:
    # 取得這個月內所有排程任務之間最大的小時數差距
    max_hours_diff = get_max_hours_diff_between(
        sign_in_job_cron, sign_out_job_cron)

    # 若排程時間大於12小時，依學校規定則此筆人事紀錄算是無效，將給予提醒
    if (max_hours_diff > 12):
        logging.warning("!!! 請注意 !!!")
        logging.warning("目前設定的簽到退排程任務間隔大於十二小時，依學校規定此類簽到記錄無效")
        logging.warning("建議檢查簽排程時間變數設定，並調整簽到退的時間點")


def validate_cron_jobs_scheduling_config(sign_in_job_cron: str, sign_out_job_cron: str) -> None:
    # 檢查此月分中所有排程任務間是否有任務間隔只有五分鐘 (重試機制所限制)
    validate_cron_jobs_overlap(sign_in_job_cron, sign_out_job_cron)

    # 檢查此月分中所有簽到退排程任務是否有任何大於12小時，若存在則給予警告提醒
    validate_cron_jobs_correctness(sign_in_job_cron, sign_out_job_cron)
