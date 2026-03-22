"""
test_14_notifications.py - 系统通知接口测试
覆盖需求：REQ-79 ~ REQ-82
"""
import requests
from config import BASE_URL

BASE = f"{BASE_URL}/api/notifications"


class TestNotifications:

    def _headers(self, token):
        return {"authorization": token}

    def test_list_all_notifications(self, zhang_token):
        """正向：查询全部通知，包含未读数量"""
        res = requests.get(f"{BASE}/", headers=self._headers(zhang_token))
        assert res.status_code == 200
        body = res.json()
        assert isinstance(body["data"], list)
        assert "unread_count" in body

    def test_list_unread_only(self, zhang_token):
        """正向：只查未读通知（unread_only=true）"""
        res = requests.get(f"{BASE}/?unread_only=true", headers=self._headers(zhang_token))
        assert res.status_code == 200
        for notif in res.json()["data"]:
            assert notif["is_read"] == 0

    def test_mark_single_read(self, zhang_token):
        """正向：标记单条通知为已读"""
        # 先查出第一条未读通知 ID
        res = requests.get(f"{BASE}/?unread_only=true", headers=self._headers(zhang_token))
        notifications = res.json()["data"]
        if not notifications:
            return  # 无未读时跳过
        notif_id = notifications[0]["id"]
        mark_res = requests.put(f"{BASE}/{notif_id}/read", headers=self._headers(zhang_token))
        assert mark_res.status_code == 200

    def test_mark_all_read(self, zhang_token):
        """正向：全部标记为已读后未读数为0"""
        requests.put(f"{BASE}/read-all", headers=self._headers(zhang_token))
        res = requests.get(f"{BASE}/", headers=self._headers(zhang_token))
        assert res.json()["unread_count"] == 0

    def test_no_token_rejected(self):
        """鉴权：无 Token 查询被拒"""
        res = requests.get(f"{BASE}/")
        assert res.status_code == 401
