from notification.notifier import Notifier
from apscheduler.events import JobExecutionEvent


# 處理排程例外狀況事件
def exception_event_handler(event: JobExecutionEvent) -> None:
    notifier = Notifier()

    if event.exception:
        notifier.notify(f"執行簽到退任務 {event.job_id} 時發生例外狀況: {event.exception}")
