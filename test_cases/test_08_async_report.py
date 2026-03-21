"""
test_08_async_report.py - 异步报表接口测试
覆盖需求：REQ-49 ~ REQ-51
- 提交报表任务立即返回 task_id（状态 processing）
- 轮询等待，最终状态变为 done
- 查询不存在的 task_id 返回 404
- 无 Token 被拒
"""
import time
import pytest
import requests
from config import BASE_URL


class TestAsyncReport:
    """异步报表生成接口测试"""

    GENERATE = f"{BASE_URL}/api/report/generate"

    def _headers(self, token):
        return {"authorization": token}

    # ── 正向：完整异步流程 ─────────────────────────────────
    def test_generate_report_returns_task_id(self, zhang_token):
        """正向：提交任务后立刻返回 task_id，状态为 processing"""
        payload = {
            "account_no": "6222020000000001",
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
        }
        res = requests.post(self.GENERATE, json=payload, headers=self._headers(zhang_token))
        assert res.status_code == 200
        data = res.json()["data"]
        assert "task_id" in data
        assert data["state"] == "processing"

    def test_poll_until_done(self, zhang_token):
        """
        异步核心测试：
        1. 提交任务
        2. 轮询直到状态变为 done（最多等 10 秒）
        3. 断言结果包含报表数据
        """
        payload = {
            "account_no": "6222020000000001",
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
        }
        # Step1: 提交任务
        res = requests.post(self.GENERATE, json=payload, headers=self._headers(zhang_token))
        task_id = res.json()["data"]["task_id"]

        # Step2: 轮询（超时 10 秒）
        poll_url = f"{BASE_URL}/api/report/{task_id}"
        final_state = None
        for _ in range(10):
            time.sleep(1)
            poll_res = requests.get(poll_url, headers=self._headers(zhang_token))
            state = poll_res.json()["data"]["state"]
            if state == "done":
                final_state = poll_res.json()["data"]
                break

        # Step3: 断言
        assert final_state is not None, "报表任务在 10 秒内未完成（超时）"
        assert final_state["state"] == "done"
        result = final_state["result"]
        assert result["account_no"] == "6222020000000001"
        assert result["transaction_count"] > 0
        assert "report_url" in result

    # ── 异常：查询不存在的任务 ────────────────────────────
    def test_get_nonexistent_task(self, zhang_token):
        """异常：查询不存在的 task_id 返回 404"""
        res = requests.get(
            f"{BASE_URL}/api/report/nonexistent-task-id-12345",
            headers=self._headers(zhang_token),
        )
        assert res.status_code == 404

    # ── 鉴权 ──────────────────────────────────────────────
    def test_generate_no_token_rejected(self):
        """鉴权：无 Token 提交报表任务被拒"""
        payload = {
            "account_no": "6222020000000001",
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
        }
        res = requests.post(self.GENERATE, json=payload)
        assert res.status_code == 401
