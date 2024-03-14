import logging
import os
import sys
import errno
from datetime import datetime


# 創建目錄，若上層目錄不存在，自動建立
def mkdir_p(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


# MakeFileHandler - 先創建所有目錄後再交由 FileHandler 開檔
class MakeFileHandler(logging.FileHandler):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""

    def __init__(self, filename, mode='a', encoding=None, delay=0):
        mkdir_p(os.path.dirname(filename))
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)


# 初始化 Logger
def init_logger(verbose: bool) -> None:
    # 指定 Logging 格式
    formatter = logging.Formatter(
        '%(asctime)s %(filename)s %(levelname)s: %(message)s')

    # 指定 Logging 檔名並創建 MakeFileHandler 來使 Logger 將 Log 存到檔案
    log_filename = f'logs/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    file_handler = MakeFileHandler(
        filename=log_filename, encoding='utf-8')

    # 設定 MakeFileHandler Logging 的格式以及等級
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # 創建 Standard Output Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)

    # 設定 Standard Output Stream Handler Logging 的格式以及等級
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # 取得 Root Logger 並設定 Logging 等級
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)

    # 將 MakeFileHandler 和 StreamHandler 附加到 Root Logger 上
    root.addHandler(file_handler)
    root.addHandler(stream_handler)
