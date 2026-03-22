"""
test_12_transaction_history.py - 交易流水查询测试
覆盖需求：REQ-69 ~ REQ-73
"""
import requests
from config import BASE_URL

BASE = f"{BASE_URL}/api/transactions"


class TestTransactionHistory:

    def _headers(self, token):
        return {"authorization": token}

    def test_history_default(self, zhang_token):
        """正向：查询全部流水（默认分页）"""
        res = requests.get(f"{BASE}/history", headers=self._headers(zhang_token))
        assert res.status_code == 200
        body = res.json()
        assert "data" in body
        assert "total" in body
        assert "total_pages" in body

    def test_history_filter_by_type(self, zhang_token):
        """正向：按交易类型过滤（只看存款记录）"""
        res = requests.get(f"{BASE}/history?txn_type=deposit", headers=self._headers(zhang_token))
        assert res.status_code == 200
        for record in res.json()["data"]:
            assert record["txn_type"] == "deposit"

    def test_history_filter_by_date(self, zhang_token):
        """正向：按日期范围过滤"""
        res = requests.get(
            f"{BASE}/history?start_date=2026-01-01&end_date=2026-12-31",
            headers=self._headers(zhang_token),
        )
        assert res.status_code == 200
        assert "data" in res.json()

    def test_history_pagination(self, zhang_token):
        """正向：分页查询（PAGE 1，每页5条）"""
        res = requests.get(f"{BASE}/history?page=1&page_size=5", headers=self._headers(zhang_token))
        assert res.status_code == 200
        assert len(res.json()["data"]) <= 5

    def test_query_other_account_rejected(self, zhang_token):
        """安全：查询不属于自己的账号流水被拒"""
        res = requests.get(
            f"{BASE}/history?account_no=6222020000000003",  # li_si 的账号
            headers=self._headers(zhang_token),
        )
        assert res.status_code == 403

    def test_no_token_rejected(self):
        """鉴权：无 Token 查询被拒"""
        res = requests.get(f"{BASE}/history")
        assert res.status_code == 401
