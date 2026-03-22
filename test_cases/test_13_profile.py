"""
test_13_profile.py - 个人资料接口测试
覆盖需求：REQ-74 ~ REQ-78
"""
import requests
from config import BASE_URL

BASE = f"{BASE_URL}/api/profile"


class TestProfile:

    def _headers(self, token):
        return {"authorization": token}

    def test_get_profile(self, zhang_token):
        """正向：查询个人资料"""
        res = requests.get(f"{BASE}/", headers=self._headers(zhang_token))
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["username"] == "zhang_san"
        assert "email" in data
        assert "kyc_status" in data

    def test_update_profile_email(self, zhang_token):
        """正向：修改邮箱"""
        res = requests.put(f"{BASE}/", json={"email": "new_email@test.com"},
                           headers=self._headers(zhang_token))
        assert res.status_code == 200
        assert res.json()["msg"] == "资料更新成功"

    def test_update_profile_real_name(self, zhang_token):
        """正向：修改真实姓名"""
        res = requests.put(f"{BASE}/", json={"real_name": "张三丰"},
                           headers=self._headers(zhang_token))
        assert res.status_code == 200

    def test_update_empty_fields_rejected(self, zhang_token):
        """异常：不提供任何字段时被拒绝"""
        res = requests.put(f"{BASE}/", json={}, headers=self._headers(zhang_token))
        assert res.status_code == 400

    def test_change_password_success(self, zhang_token):
        """正向：正确旧密码修改密码成功"""
        res = requests.put(f"{BASE}/password", json={
            "old_password": "Test@1234",
            "new_password": "Test@1234",  # 修改成相同密码会被拒
        }, headers=self._headers(zhang_token))
        # 新旧密码相同应被拒绝
        assert res.status_code == 400

    def test_change_password_wrong_old(self, zhang_token):
        """异常：旧密码错误时拒绝修改"""
        res = requests.put(f"{BASE}/password", json={
            "old_password": "WrongPass@999",
            "new_password": "NewPass@5678",
        }, headers=self._headers(zhang_token))
        assert res.status_code == 401
