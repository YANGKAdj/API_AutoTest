"""
test_10_loan.py - 贷款中心接口测试
覆盖需求：REQ-55 ~ REQ-62
"""
import pytest
import requests
from config import BASE_URL

BASE = f"{BASE_URL}/api/loan"


class TestLoan:

    def _headers(self, token):
        return {"authorization": token}

    # ── 正向：申请贷款全流程 ──────────────────────────────
    def test_apply_loan_success(self, zhang_token):
        """正向：合法申请贷款，系统自动放款"""
        res = requests.post(f"{BASE}/apply", json={
            "account_no": "6222020000000001",
            "amount": 10000,
            "term_months": 12,
            "purpose": "装修",
        }, headers=self._headers(zhang_token))
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["loan_id"].startswith("LOAN")
        assert data["monthly_payment"] > 0
        assert data["status"] == "active"

    def test_loan_list(self, zhang_token):
        """正向：查询贷款列表"""
        res = requests.get(f"{BASE}/list", headers=self._headers(zhang_token))
        assert res.status_code == 200
        assert isinstance(res.json()["data"], list)

    def test_loan_detail(self, zhang_token):
        """正向：查询贷款详情（先申请再查）"""
        # 先申请
        apply_res = requests.post(f"{BASE}/apply", json={
            "account_no": "6222020000000001",
            "amount": 5000,
            "term_months": 6,
            "purpose": "医疗",
        }, headers=self._headers(zhang_token))
        loan_id = apply_res.json()["data"]["loan_id"]

        # 再查详情
        res = requests.get(f"{BASE}/{loan_id}", headers=self._headers(zhang_token))
        assert res.status_code == 200
        assert res.json()["data"]["loan_id"] == loan_id

    def test_repay_loan_success(self, zhang_token):
        """正向：还款成功，剩余本金减少"""
        # 申请贷款
        apply_res = requests.post(f"{BASE}/apply", json={
            "account_no": "6222020000000001",
            "amount": 6000,
            "term_months": 12,
            "purpose": "消费",
        }, headers=self._headers(zhang_token))
        loan_id = apply_res.json()["data"]["loan_id"]

        # 还款
        res = requests.post(f"{BASE}/{loan_id}/repay", json={
            "account_no": "6222020000000001",
            "amount": 1000,
        }, headers=self._headers(zhang_token))
        assert res.status_code == 200
        assert res.json()["data"]["remaining"] < 6000

    # ── 异常用例 ─────────────────────────────────────────
    def test_loan_invalid_term(self, zhang_token):
        """异常：不支持的贷款期限"""
        res = requests.post(f"{BASE}/apply", json={
            "account_no": "6222020000000001",
            "amount": 5000,
            "term_months": 18,  # 不支持
            "purpose": "测试",
        }, headers=self._headers(zhang_token))
        assert res.status_code == 400

    def test_repay_exceeds_remaining(self, zhang_token):
        """异常：还款金额超过剩余本金"""
        apply_res = requests.post(f"{BASE}/apply", json={
            "account_no": "6222020000000001",
            "amount": 3000,
            "term_months": 3,
            "purpose": "测试",
        }, headers=self._headers(zhang_token))
        loan_id = apply_res.json()["data"]["loan_id"]

        res = requests.post(f"{BASE}/{loan_id}/repay", json={
            "account_no": "6222020000000001",
            "amount": 99999,  # 超额
        }, headers=self._headers(zhang_token))
        assert res.status_code == 400

    def test_loan_no_token(self):
        """鉴权：无 Token 申请贷款被拒"""
        res = requests.post(f"{BASE}/apply", json={
            "account_no": "6222020000000001",
            "amount": 5000,
            "term_months": 12,
            "purpose": "测试",
        })
        assert res.status_code == 401
