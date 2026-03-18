"""
test_04_transfer.py - 转账功能测试（数据驱动版本）

测试数据全部来自 data/bank_test_data.yaml，体现"测试数据与测试逻辑分离"的设计原则。
"""
import pytest
from api.account_api import AccountAPI
from api.transaction_api import TransactionAPI
from utils.yaml_util import read_yaml

_data = read_yaml("bank_test_data.yaml")
transfer_cases       = _data["transfer"]
cross_transfer_cases = _data["cross_transfer"]


def get_code(res) -> int:
    """成功响应 code 在顶层，错误响应 code 在 detail 里"""
    body = res.json()
    if res.status_code < 400:
        return body["code"]
    else:
        return body["detail"]["code"]


class TestTransfer:
    """行内转账测试 - YAML 数据驱动"""

    @pytest.mark.parametrize("case", transfer_cases, ids=[c["case"] for c in transfer_cases])
    def test_transfer_ddt(self, zhang_token, case):
        """参数化行内转账测试"""
        res = TransactionAPI(zhang_token).transfer(
            case["from_account"],
            case["to_account"],
            case["amount"],
            case.get("remark")
        )
        assert res.status_code == case["expected_http"], \
            f"[{case['case']}] 期望 HTTP {case['expected_http']}，实际 {res.status_code}，响应：{res.text}"

        if case["expected_code"]:
            assert get_code(res) == case["expected_code"]

    def test_transfer_double_balance_consistency(self, zhang_token):
        """
        转账双边余额一致性验证（API层 + 数据库层双重断言）：

        【为什么要加数据库校验？】
        接口返回 200 不等于数据库真的写成功了。
        金融场景中可能存在"接口报成功但事务被回滚"的隐性 bug。
        只有直连 MySQL 查到真实余额，才是对账实不符问题的最终防线。
        """
        from utils.db_util import db
        from_acc = "6222020000000001"
        to_acc   = "6222020000000003"
        amount   = 800.00

        zhang_account_api = AccountAPI(zhang_token)
        t_api = TransactionAPI(zhang_token)

        # --- 转账前：同时从 API 和 DB 两个维度记录快照 ---
        before_api = zhang_account_api.get_balance(from_acc).json()["data"]["balance"]
        before_db  = float(db.query_one(
            "SELECT balance FROM bank_accounts WHERE account_no = %s", (from_acc,)
        )["balance"])

        # --- 执行转账 ---
        res = t_api.transfer(from_acc, to_acc, amount, remark="DB一致性验证")
        assert res.status_code == 200, f"转账失败：{res.text}"
        txn_id = res.json()["txn_id"]

        # --- 转账后：API 层断言 ---
        after_api = zhang_account_api.get_balance(from_acc).json()["data"]["balance"]
        assert after_api == round(before_api - amount, 2), \
            f"【API层】付款方余额异常！转账前：{before_api}，转账后：{after_api}，差额应为：{amount}"

        # --- 转账后：数据库层断言（直连 MySQL 验证真实数据）---
        after_db = float(db.query_one(
            "SELECT balance FROM bank_accounts WHERE account_no = %s", (from_acc,)
        )["balance"])
        assert after_db == round(before_db - amount, 2), \
            f"【DB层】付款方余额异常！DB中转账前：{before_db}，转账后：{after_db}，差额应为：{amount}"

        # --- 验证流水记录确实写入了 transactions 表 ---
        txn_record = db.query_one(
            "SELECT * FROM transactions WHERE txn_id = %s", (txn_id,)
        )
        assert txn_record is not None, f"数据库中未找到转账流水记录！txn_id={txn_id}"
        assert txn_record["txn_type"]    == "transfer"
        assert txn_record["from_account"] == from_acc
        assert txn_record["to_account"]   == to_acc
        assert float(txn_record["amount"]) == amount



class TestCrossBankTransfer:
    """跨行转账测试 - YAML 数据驱动"""

    @pytest.mark.parametrize("case", cross_transfer_cases,
                             ids=[c["case"] for c in cross_transfer_cases])
    def test_cross_transfer_ddt(self, zhang_token, case):
        """参数化跨行转账测试，同时验证手续费计算是否准确"""
        res = TransactionAPI(zhang_token).cross_bank_transfer(
            case["from_account"],
            case["to_bank_code"],
            case["to_account"],
            case["amount"]
        )
        assert res.status_code == case["expected_http"], \
            f"[{case['case']}] 期望 HTTP {case['expected_http']}，实际 {res.status_code}，响应：{res.text}"

        # 只有成功的用例才验证手续费
        if case["expected_fee"] is not None:
            assert res.json()["fee"] == case["expected_fee"], \
                f"[{case['case']}] 手续费计算错误！期望 {case['expected_fee']}，实际 {res.json()['fee']}"
