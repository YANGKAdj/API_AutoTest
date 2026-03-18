"""
API Object 封装层 - 交易模块（transaction_api.py）
"""
import requests
from config import DEPOSIT_URL, WITHDRAW_URL, TRANSFER_URL, CROSS_TRANSFER_URL, HISTORY_URL
from utils.logger import log


class TransactionAPI:
    def __init__(self, token: str):
        self.headers = {"token": token, "Content-Type": "application/json"}

    def deposit(self, account_no: str, amount: float):
        payload = {"account_no": account_no, "amount": amount}
        log.info(f"[存款] account={account_no}, amount={amount}")
        res = requests.post(DEPOSIT_URL, json=payload, headers=self.headers)
        log.info(f"[存款] 响应: {res.status_code} {res.json()}")
        return res

    def withdraw(self, account_no: str, amount: float):
        payload = {"account_no": account_no, "amount": amount}
        log.info(f"[取款] account={account_no}, amount={amount}")
        res = requests.post(WITHDRAW_URL, json=payload, headers=self.headers)
        log.info(f"[取款] 响应: {res.status_code} {res.json()}")
        return res

    def transfer(self, from_account: str, to_account: str, amount: float, remark: str = None):
        payload = {"from_account": from_account, "to_account": to_account,
                   "amount": amount, "remark": remark}
        log.info(f"[行内转账] {from_account} → {to_account}, amount={amount}")
        res = requests.post(TRANSFER_URL, json=payload, headers=self.headers)
        log.info(f"[行内转账] 响应: {res.status_code} {res.json()}")
        return res

    def cross_bank_transfer(self, from_account: str, to_bank_code: str,
                            to_account: str, amount: float):
        payload = {"from_account": from_account, "to_bank_code": to_bank_code,
                   "to_account": to_account, "amount": amount}
        log.info(f"[跨行转账] {from_account} → {to_bank_code}:{to_account}, amount={amount}")
        res = requests.post(CROSS_TRANSFER_URL, json=payload, headers=self.headers)
        log.info(f"[跨行转账] 响应: {res.status_code} {res.json()}")
        return res

    def get_history(self, account_no: str, page: int = 1, size: int = 10):
        params = {"account_no": account_no, "page": page, "size": size}
        log.info(f"[查询记录] account={account_no}, page={page}")
        res = requests.get(HISTORY_URL, params=params, headers=self.headers)
        log.info(f"[查询记录] 响应: {res.status_code} {res.json()}")
        return res
