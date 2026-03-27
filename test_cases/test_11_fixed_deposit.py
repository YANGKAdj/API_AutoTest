"""
test_11_fixed_deposit.py - 定期存款接口测试
覆盖需求：REQ-63 ~ REQ-68
"""
import pytest
import requests
from config import BASE_URL

BASE = f"{BASE_URL}/api/fixed-deposit"


class TestFixedDeposit:

    def _headers(self, token):
        return {"authorization": token}

    # ── 正向 ─────────────────────────────────────────────
    def test_create_fixed_deposit_success(self, zhang_token):
        """正向：开立12个月定期，余额扣减，年利率正确"""
        # 确保余额充足
        requests.post(f"{BASE_URL}/api/transaction/deposit", json={
            "account_no": "6222020000000002", "amount": 2000
        }, headers={"token": zhang_token})
        
        res = requests.post(f"{BASE}/create", json={
            "account_no": "6222020000000002",
            "amount": 2000,
            "term_months": 12,
        }, headers=self._headers(zhang_token))
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["fd_id"].startswith("FD")
        assert data["annual_rate"] == "2.50%"
        assert data["interest"] == round(2000 * 0.0250 * 12 / 12, 2)

    def test_list_fixed_deposits(self, zhang_token):
        """正向：查询定期列表"""
        res = requests.get(f"{BASE}/list", headers=self._headers(zhang_token))
        assert res.status_code == 200
        assert isinstance(res.json()["data"], list)

    def test_early_withdraw(self, zhang_token):
        """正向：提前支取，返还本金（利息按活期利率重算）"""
        # 先确保余额充足
        requests.post(f"{BASE_URL}/api/transaction/deposit", json={
            "account_no": "6222020000000002", "amount": 2000
        }, headers={"token": zhang_token})
        
        # 先开立一笔定期
        create_res = requests.post(f"{BASE}/create", json={
            "account_no": "6222020000000002",
            "amount": 1000,
            "term_months": 6,
        }, headers=self._headers(zhang_token))
        fd_id = create_res.json()["data"]["fd_id"]

        # 提前支取
        res = requests.post(f"{BASE}/{fd_id}/withdraw", headers=self._headers(zhang_token))
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["principal"] == 1000
        assert data["lost_interest"] >= 0  # 损失利息应 >= 0

    # ── 异常 ─────────────────────────────────────────────
    def test_invalid_term_months(self, zhang_token):
        """异常：不支持的期限（2个月）"""
        res = requests.post(f"{BASE}/create", json={
            "account_no": "6222020000000002",
            "amount": 1000,
            "term_months": 2,
        }, headers=self._headers(zhang_token))
        assert res.status_code == 400

    def test_insufficient_balance(self, zhang_token):
        """异常：余额不足时不允许开立定期"""
        res = requests.post(f"{BASE}/create", json={
            "account_no": "6222020000000002",
            "amount": 999999,  # 远超余额但符合框架边界金额约束(<=1,000,000)
            "term_months": 12,
        }, headers=self._headers(zhang_token))
        assert res.status_code == 400

    def test_double_withdraw_rejected(self, zhang_token):
        """异常：已支取的定期不允许再次支取"""
        requests.post(f"{BASE_URL}/api/transaction/deposit", json={
            "account_no": "6222020000000002", "amount": 1000
        }, headers={"token": zhang_token})
        
        create_res = requests.post(f"{BASE}/create", json={
            "account_no": "6222020000000002",
            "amount": 500,
            "term_months": 1,
        }, headers=self._headers(zhang_token))
        fd_id = create_res.json()["data"]["fd_id"]

        requests.post(f"{BASE}/{fd_id}/withdraw", headers=self._headers(zhang_token))
        # 再次支取应被拒绝
        res = requests.post(f"{BASE}/{fd_id}/withdraw", headers=self._headers(zhang_token))
        assert res.status_code == 400
