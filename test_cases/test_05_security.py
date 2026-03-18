"""
test_05_security.py - 安全测试
覆盖：无 Token 访问、Token 伪造、越权访问（IDOR）、参数篡改、SQL 注入防护
"""
import pytest
from api.account_api import AccountAPI
from api.transaction_api import TransactionAPI
from api.auth_api import AuthAPI

auth_api = AuthAPI()


class TestAuthSecurity:
    """鉴权安全测试"""

    def test_no_token_access(self):
        """无 Token 访问受保护接口应返回 401"""
        api = AccountAPI(token="")
        res = api.get_account("6222020000000001")
        assert res.status_code == 401

    def test_invalid_token_format(self):
        """伪造/格式错误的 Token 应返回 401"""
        api = AccountAPI(token="fake_token_12345")
        res = api.get_account("6222020000000001")
        assert res.status_code == 401

    def test_account_lockout_after_5_failures(self):
        """
        账户连续失败 5 次后被锁定：
        第 5 次应返回 423（Locked），此后任意密码都无法登录
        """
        # 使用 temp_user 注册一个新用户专门用于锁定测试
        import random
        n = random.randint(200000, 299999)
        username = f"locktest_{n}"
        phone    = f"1590000{str(n)[:4]}"
        auth_api.register(username, "Test@1234", phone)

        for i in range(4):
            res = auth_api.login(username, "WrongPwd!")
            assert res.status_code == 401

        # 第 5 次失败，账户应该被锁定
        res = auth_api.login(username, "WrongPwd!")
        assert res.status_code == 423

        # 锁定后正确密码也无法登录
        res_correct = auth_api.login(username, "Test@1234")
        assert res_correct.status_code == 423


class TestIDOR:
    """越权访问测试（IDOR - Insecure Direct Object Reference）"""

    def test_access_other_user_account(self, li_token):
        """
        li_si 尝试用自己的 Token 查询 zhang_san 的账户详情
        预期：返回 403，彻底杜绝越权
        """
        api = AccountAPI(li_token)
        res = api.get_account("6222020000000001")  # zhang_san 的账户
        assert res.status_code == 403
        assert res.json()["detail"]["code"] == 403

    def test_withdraw_from_other_user_account(self, li_token):
        """
        li_si 尝试从 zhang_san 账户中取款
        预期：返回 403
        """
        api = TransactionAPI(li_token)
        res = api.withdraw("6222020000000001", 100.00)
        assert res.status_code == 403

    def test_transfer_from_other_user_account(self, li_token):
        """
        li_si 尝试用自己的 Token 从 zhang_san 账户转账
        预期：返回 403
        """
        api = TransactionAPI(li_token)
        res = api.transfer("6222020000000001", "6222020000000003", 100.00)
        assert res.status_code == 403


class TestParameterTampering:
    """参数篡改测试"""

    def test_negative_deposit_amount(self, zhang_token):
        """存款金额为负数，应被 Pydantic 拦截，返回 422"""
        api = TransactionAPI(zhang_token)
        res = api.deposit("6222020000000001", -1000.00)
        assert res.status_code == 422

    def test_negative_transfer_amount(self, zhang_token):
        """转账金额为负数，应返回 422"""
        api = TransactionAPI(zhang_token)
        res = api.transfer("6222020000000001", "6222020000000003", -500.00)
        assert res.status_code == 422


class TestSQLInjection:
    """SQL 注入防护测试（PyMySQL 参数化查询保障）"""

    def test_sql_injection_in_username(self):
        """
        在用户名字段传入 SQL 注入语句
        预期：接口正常返回 401（未绕过登录），而非崩溃或返回数据
        """
        res = auth_api.login("' OR 1=1 --", "anything")
        assert res.status_code == 401
        # 关键：不能返回 200，证明注入未成功

    def test_sql_injection_report_content(self):
        """确认响应体不包含数据库错误信息（防止信息泄露）"""
        res = auth_api.login("' OR '1'='1", "' OR '1'='1")
        assert "syntax" not in res.text.lower()
        assert "mysql"  not in res.text.lower()
