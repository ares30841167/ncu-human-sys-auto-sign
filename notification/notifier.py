from notification.discord import Discord


class Notifier():
    def __init__(self):
        # 初始化所有通知通道
        self.notifers = [Discord()]

    # 傳送通知
    def notify(self, msg: str) -> None:
        # 對所有通道傳送訊息
        for notifer in self.notifers:
            notifer.notify(msg)
