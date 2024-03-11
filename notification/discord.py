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
                raise Exception("未設定環境變數 DISCORD_WEBHOOK_URL")

            # 檢查 DISCORD_WEBHOOK_URL 是否為空
            if (os.environ.get("DISCORD_WEBHOOK_URL") == ""):
                raise Exception("DISCORD_WEBHOOK_URL不得為空")
            
            # 設定 Webhook URL
            self.webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    def notify(self, msg: str) -> None:
        requests.post(self.webhook_url, json={"content": msg})
        logging.debug(
            f"已透過 Webhook URL {self.webhook_url} 請 Discord 送出頻道訊息: {msg}")
