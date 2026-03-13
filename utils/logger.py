import logging
import os
import time


def get_logger():
    logger = logging.getLogger("Arsenal_Logger")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        # 日志格式：时间 - 级别 - 文件名[行号] - 日志内容
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s[line:%(lineno)d] - %(message)s')

        # 1. 输出到控制台
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        # 2. 输出到文件 (每天生成一个新日志文件)
        log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        if not os.path.exists(log_path): os.mkdir(log_path)
        log_name = os.path.join(log_path, f"test_{time.strftime('%Y%m%d')}.log")

        fh = logging.FileHandler(log_name, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


log = get_logger()
