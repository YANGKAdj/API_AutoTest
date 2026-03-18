"""
test_02_account.py - 账户管理功能测试
覆盖：开户、查询账户详情、查询余额、注销账户
"""
import pytest
from api.account_api import AccountAPI
from api.transaction_api import TransactionAPI


class TestAccount:
    """账户管理测试"""

    def test_create_savings_account(self, zhang_token):
        """正向：开立储蓄账户，返回 16 位账号"""
        api = AccountAPI(zhang_token)
        res = api.create_account("savings")
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == 200
        assert len(data["account_no"]) == 16

    def test_create_current_account(self, zhang_token):
        """正向：开立活期账户"""
        api = AccountAPI(zhang_token)
        res = api.create_account("current")
        assert res.status_code == 200

    def test_create_invalid_account_type(self, zhang_token):
        """异常：账户类型不合法应返回 400"""
        api = AccountAPI(zhang_token)
        res = api.create_account("invalid_type")
        assert res.status_code == 400

    def test_get_account_detail(self, zhang_token):
        """正向：查询本人账户详情，返回 balance 和 status"""
        api = AccountAPI(zhang_token)
        res = api.get_account("6222020000000001")
        assert res.status_code == 200
        data = res.json()["data"]
        assert "balance" in data
        assert data["status"] == "active"

    def test_get_balance(self, zhang_token):
        """正向：查询余额，返回数值类型"""
        api = AccountAPI(zhang_token)
        res = api.get_balance("6222020000000001")
        assert res.status_code == 200
        assert isinstance(res.json()["data"]["balance"], float)

    def test_close_account_with_zero_balance(self, zhang_token):
        """正向：余额为 0 的账户可以注销"""
        api = AccountAPI(zhang_token)
        # 先开户
        create_res = api.create_account("savings")
        account_no = create_res.json()["account_no"]
        # 注销
        close_res = api.close_account(account_no)
        assert close_res.status_code == 200

    def test_close_account_with_balance(self, zhang_token):
        """异常：余额不为 0 的账户不能注销，应返回 400"""
        api = AccountAPI(zhang_token)
        res = api.close_account("6222020000000001")  # balance=50000
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == 400

    def test_get_nonexistent_account(self, zhang_token):
        """异常：查询不存在的账户应返回 404"""
        api = AccountAPI(zhang_token)
        res = api.get_account("0000000000000000")
        assert res.status_code == 404
