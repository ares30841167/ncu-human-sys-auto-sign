import os
import logging
import requests


class Discord():
    def __init__(self, webhook_url: str = ""):
        if (webhook_url != ""):
            # 從建構子傳入參數設定 Webhook URL
            self.webhook_url = webhook_url
        else:
            # 檢查 DISCORD_WEBHOOK_URL 是否存在 .env 內
            if ("DISCORD_WEBHOOK_URL" not in os.environ):
                # 停用 Discord 通知通道
                self.enabled = False
                logging.info("未設定環境變數 DISCORD_WEBHOOK_URL，停用 Discord 通知通道")

                return

            # 檢查 DISCORD_WEBHOOK_URL 是否為空
            if (os.environ.get("DISCORD_WEBHOOK_URL") == ""):
                # 停用 Discord 通知通道
                self.enabled = False
                logging.info("環境變數 DISCORD_WEBHOOK_URL 為空，停用 Discord 通知通道")

                return

            # 設定 Webhook URL
            self.webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

        # 啟用此通知通道
        self.enabled = True
        logging.info("已啟用 Discord 通知通道")

    def notify(self, msg: str) -> None:
        # 未啟用此通知通道時，直接返回不作動
        if(not self.enabled): return

        # 傳送通知訊息
        try:
            requests.post(self.webhook_url, json={"content": msg})
            logging.debug(
                f"已透過 Webhook URL {self.webhook_url} 請 Discord 送出頻道訊息: {msg}")
        except Exception:
            logging.exception(f"透過 Discord 送出頻道訊息 {msg} 時發生錯誤")
