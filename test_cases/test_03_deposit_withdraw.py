"""
test_03_deposit_withdraw.py - 存取款功能测试（数据驱动版本）

测试数据全部来自 data/bank_test_data.yaml，
测试脚本只负责"发请求+断言"，不硬编码任何参数值。
这是数据驱动测试（DDT）的核心思想：测试逻辑与测试数据完全分离。
"""
import pytest
from api.account_api import AccountAPI
from api.transaction_api import TransactionAPI
from utils.yaml_util import read_yaml

# 在模块加载时读取 YAML，只读一次
_data = read_yaml("bank_test_data.yaml")
deposit_cases  = _data["deposit"]
withdraw_cases = _data["withdraw"]


def get_code(res) -> int:
    """
    统一提取业务 code 字段的工具函数。
    
    FastAPI 的响应有两种格式：
    - 成功：{"code": 200, "msg": "..."} → code 在顶层
    - 异常：{"detail": {"code": 400, "msg": "..."}} → code 在 detail 里
    
    用 HTTP 状态码来判断从哪里取：
    """
    body = res.json()
    if res.status_code < 400:
        return body["code"]       # 成功响应，code 在顶层
    else:
        return body["detail"]["code"]  # 异常响应，code 在 detail 里


class TestDeposit:
    """存款测试 - YAML 数据驱动"""

    @pytest.mark.parametrize("case", deposit_cases, ids=[c["case"] for c in deposit_cases])
    def test_deposit_ddt(self, zhang_token, case):
        res = TransactionAPI(zhang_token).deposit(case["account_no"], case["amount"])
        assert res.status_code == case["expected_http"], \
            f"[{case['case']}] 期望 HTTP {case['expected_http']}，实际 {res.status_code}，响应：{res.text}"

        if case["expected_code"]:
            assert get_code(res) == case["expected_code"]

    def test_deposit_balance_consistency(self, zhang_token):
        """
        单独验证余额一致性：
        存款前查余额 → 存款 → 存款后查余额 → 断言精确等于（存款前 + 存入金额）
        这是数据库一致性校验的体现，不放在参数化里是因为需要前后两次查询。
        """
        account_no = "6222020000000002"
        a_api = AccountAPI(zhang_token)
        t_api = TransactionAPI(zhang_token)

        before = a_api.get_balance(account_no).json()["data"]["balance"]
        amount = 500.00
        t_api.deposit(account_no, amount)
        after = a_api.get_balance(account_no).json()["data"]["balance"]

        assert after == round(before + amount, 2), \
            f"余额不一致！存款前：{before}，存入：{amount}，期望：{round(before+amount,2)}，实际：{after}"


class TestWithdraw:
    """取款测试 - YAML 数据驱动"""

    @pytest.mark.parametrize("case", withdraw_cases, ids=[c["case"] for c in withdraw_cases])
    def test_withdraw_ddt(self, zhang_token, case):
        """参数化取款测试"""
        res = TransactionAPI(zhang_token).withdraw(case["account_no"], case["amount"])
        assert res.status_code == case["expected_http"], \
            f"[{case['case']}] 期望 HTTP {case['expected_http']}，实际 {res.status_code}，响应：{res.text}"

        if case["expected_code"]:
            assert get_code(res) == case["expected_code"]

    def test_withdraw_balance_consistency(self, zhang_token):
        """取款余额一致性验证"""
        account_no = "6222020000000001"
        a_api = AccountAPI(zhang_token)
        t_api = TransactionAPI(zhang_token)

        before = a_api.get_balance(account_no).json()["data"]["balance"]
        amount = 300.00
        t_api.withdraw(account_no, amount)
        after = a_api.get_balance(account_no).json()["data"]["balance"]

        assert after == round(before - amount, 2), \
            f"余额不一致！取款前：{before}，取出：{amount}，期望：{round(before-amount,2)}，实际：{after}"
