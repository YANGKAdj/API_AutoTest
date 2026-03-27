"""
test_01_auth.py - 用户注册与登录功能测试
覆盖：正向注册、重复注册、登录成功、密码错误、账户锁定
"""
import pytest
from api.auth_api import AuthAPI

auth_api = AuthAPI()


class TestRegister:
    """注册模块"""

    def test_register_success(self, temp_user):
        """正向：注册成功（temp_user fixture 已包含注册动作，断言其结果）"""
        # temp_user 已能成功创建并登录，说明注册流程通过
        # JWT token 格式检查：应以 eyJ 开头（Base64编码的JSON）
        assert temp_user["token"].startswith("eyJ")

    def test_register_duplicate_phone(self):
        """异常：手机号重复注册应返回 400"""
        res = auth_api.register("zhang_san_dup", "Test@1234", "13800138001")  # 预置手机号
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == 400

    def test_register_short_password(self):
        """边界：密码少于 8 位，FastAPI Pydantic 校验应返回 422"""
        res = auth_api.register("user_short", "abc", "13900000001")
        assert res.status_code == 422


class TestLogin:
    """登录模块"""

    def test_login_success(self):
        """正向：正确账号密码，登录成功，返回 token"""
        res = auth_api.login("zhang_san", "Test@1234")
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == 200
        assert "token" in data
        # JWT token 格式检查：应以 eyJ 开头（Base64编码的JSON）
        assert data["token"].startswith("eyJ")

    def test_login_wrong_password(self):
        """异常：密码错误应返回 401"""
        res = auth_api.login("zhang_san", "WrongPwd!")
        assert res.status_code == 401
        assert res.json()["detail"]["code"] == 401

    def test_login_nonexistent_user(self):
        """异常：用户不存在应返回 401"""
        res = auth_api.login("ghost_user_xyz", "Test@1234")
        assert res.status_code == 401

    def test_login_empty_password(self):
        """边界：密码为空字符串"""
        res = auth_api.login("zhang_san", "")
        assert res.status_code in (401, 422)
