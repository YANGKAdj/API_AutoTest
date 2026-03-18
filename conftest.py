"""
公共的配置文件
conftest.py - Pytest 全局 Fixture 配置
提供：全局 Token、动态账户注册、数据清理
"""
import random
import pytest
from api.auth_api import AuthAPI
from utils.db_util import db

auth_api = AuthAPI()


def rand_user():
    """生成随机注册信息，避免重复"""
    n = random.randint(10000, 99999)
    return {
        "username": f"test_user_{n}",
        "password": "Test@1234",
        "phone":    f"1380013{n}"[:11]
    }


@pytest.fixture(scope="session")
def zhang_token():
    """
    会话级 Token（scope=session）：只请求一次登录，全部用例复用。
    使用预置的 zhang_san 账户（已在 init.sql 初始化）。
    """
    res = auth_api.login("zhang_san", "Test@1234")
    assert res.status_code == 200, f"前置登录失败: {res.text}"
    token = res.json()["token"]
    return token


@pytest.fixture(scope="session")
def li_token():
    """li_si 的 Token（用于越权测试）"""
    res = auth_api.login("li_si", "Test@1234")
    assert res.status_code == 200
    return res.json()["token"]


@pytest.fixture(scope="function")
def temp_user():
    """
    函数级 Fixture：每个用例创建一个独立的临时用户并登录，
    yield 之前：注册 + 登录，把 token/username/user_id 送给用例
    yield 之后：自动清理该用户在 DB 里的数据，避免脏数据积累
    """
    user_info = rand_user()
    res = auth_api.register(**user_info)
    assert res.status_code == 200, f"临时用户注册失败: {res.text}"

    login_res = auth_api.login(user_info["username"], user_info["password"])
    token   = login_res.json()["token"]
    user_id = login_res.json()["user_id"]   # ← 单独提出来，yield 后面才能用

    yield {"token": token, "username": user_info["username"], "user_id": user_id}

    # 用例跑完后自动清理（yield 之后的代码在用例结束后执行）
    db.execute("DELETE FROM bank_accounts WHERE user_id = %s", (user_id,))
    db.execute("DELETE FROM users WHERE id = %s", (user_id,))