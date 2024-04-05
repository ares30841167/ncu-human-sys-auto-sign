import datetime
from notification.notifier import Notifier
from utils.job_id import remove_job_id_retry_suffix
from apscheduler.events import JobExecutionEvent
from apscheduler.schedulers.background import BackgroundScheduler


class APSchedulerEventHandler:
    def __init__(self, scheduler: BackgroundScheduler, notifier: Notifier):
        self.retry_cnt = 5
        self.notifier = notifier
        self.scheduler = scheduler

    # 處理排程例外狀況事件
    def exception_event_handler(self, event: JobExecutionEvent) -> None:
        if event.exception:
            # 處理並取得失敗任務的原始ID
            failed_job_id = remove_job_id_retry_suffix(event.job_id)

            # 若重試次數用完歸零
            if (self.retry_cnt == 0):
                # 通知重試次數已達上限後便不再重新排程
                self.notifier.notify(f"執行簽到退任務 {failed_job_id} 重試次數已達上限")
                # 重設重試次數
                self.retry_cnt = 5
                return

            # 失敗時發出通知
            self.notifier.notify(
                f"執行簽到退任務 {failed_job_id} 時發生例外狀況: {event.exception}")
            self.notifier.notify(f"簽到退任務 {failed_job_id} 將在 1 分鐘後重試...")

            # 計算下一次重試的時間
            next_retry_time = event.scheduled_run_time + \
                datetime.timedelta(minutes=1)

            # 為失敗的任務重新排程
            failed_job = self.scheduler.get_job(failed_job_id)
            self.scheduler.add_job(failed_job.func, args=failed_job.args, trigger="date",
                                   run_date=next_retry_time, id=f"{failed_job.id}_retry")

            # 將重試嘗試次數減一
            self.retry_cnt -= 1

    # 處理排程執行成功事件
    def success_event_handler(self, event: JobExecutionEvent) -> None:
        # 成功時重設重試次數
        self.retry_cnt = 5

        # 傳送排程任務結果至各通知頻道
        self.notifier.notify(event.retval)
