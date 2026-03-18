"""
API Object 封装层 - 账户模块（account_api.py）
"""
import requests
from config import CREATE_ACCOUNT_URL, ACCOUNT_DETAIL_URL, BALANCE_URL, CLOSE_ACCOUNT_URL
from utils.logger import log


class AccountAPI:
    def __init__(self, token: str):
        self.headers = {"token": token, "Content-Type": "application/json"}

    def create_account(self, account_type: str = "savings"):
        payload = {"account_type": account_type}
        log.info(f"[开户] 类型={account_type}")
        res = requests.post(CREATE_ACCOUNT_URL, json=payload, headers=self.headers)
        log.info(f"[开户] 响应: {res.status_code} {res.json()}")
        return res

    def get_account(self, account_no: str):
        log.info(f"[查询账户] account_no={account_no}")
        res = requests.get(f"{ACCOUNT_DETAIL_URL}/{account_no}", headers=self.headers)
        log.info(f"[查询账户] 响应: {res.status_code} {res.json()}")
        return res

    def get_balance(self, account_no: str):
        log.info(f"[查询余额] account_no={account_no}")
        res = requests.get(f"{BALANCE_URL}/{account_no}", headers=self.headers)
        log.info(f"[查询余额] 响应: {res.status_code} {res.json()}")
        return res

    def close_account(self, account_no: str):
        log.info(f"[注销账户] account_no={account_no}")
        res = requests.post(f"{CLOSE_ACCOUNT_URL}/{account_no}", headers=self.headers)
        log.info(f"[注销账户] 响应: {res.status_code} {res.json()}")
        return res
