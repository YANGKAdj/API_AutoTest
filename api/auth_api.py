"""
API Object 封装层 - 认证模块（auth_api.py）
封装注册和登录接口，供测试用例层调用
"""
import requests
from config import REGISTER_URL, LOGIN_URL
from utils.logger import log


class AuthAPI:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    def register(self, username: str, password: str, phone: str):
        payload = {"username": username, "password": password, "phone": phone}
        log.info(f"[注册] 发起注册请求: username={username}, phone={phone}")
        res = requests.post(REGISTER_URL, json=payload, headers=self.headers)
        log.info(f"[注册] 响应: {res.status_code} {res.json()}")
        return res

    def login(self, username: str, password: str):
        payload = {"username": username, "password": password}
        log.info(f"[登录] 发起登录请求: username={username}")
        res = requests.post(LOGIN_URL, json=payload, headers=self.headers)
        log.info(f"[登录] 响应: {res.status_code} {res.json()}")
        return res
