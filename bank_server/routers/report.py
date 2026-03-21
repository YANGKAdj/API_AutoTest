"""
异步报表模块 - 模拟银行账单报告异步生成接口
POST /api/report/generate  → 返回 task_id
GET  /api/report/{task_id} → 轮询任务状态
"""
import uuid
import time
import threading
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

router = APIRouter(prefix="/api/report", tags=["异步报表"])

# 内存存储任务状态（生产环境应使用 Redis）
_task_store: dict = {}


class ReportRequest(BaseModel):
    account_no: str
    start_date: str  # 格式: "2026-01-01"
    end_date: str    # 格式: "2026-03-31"


def _verify_token(token: str):
    if not token or not token.startswith("BANK_TOKEN_"):
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 无效"})


def _generate_report_async(task_id: str, account_no: str):
    """后台线程：模拟耗时的报表生成过程（2秒）"""
    time.sleep(2)
    _task_store[task_id] = {
        "task_id": task_id,
        "state": "done",
        "result": {
            "account_no": account_no,
            "total_deposit": 50000.00,
            "total_withdraw": 12000.00,
            "total_transfer": 8000.00,
            "transaction_count": 42,
            "report_url": f"/reports/{task_id}.pdf",
        },
    }


@router.post("/generate")
def generate_report(body: ReportRequest, authorization: str = Header(None)):
    """
    异步生成账单报表（立即返回 task_id，后台处理）
    """
    _verify_token(authorization)

    task_id = str(uuid.uuid4())
    _task_store[task_id] = {"task_id": task_id, "state": "processing"}

    # 启动后台线程处理报表
    t = threading.Thread(
        target=_generate_report_async,
        args=(task_id, body.account_no),
        daemon=True,
    )
    t.start()

    return {
        "code": 200,
        "msg": "报表生成任务已提交，请轮询任务状态",
        "data": {"task_id": task_id, "state": "processing"},
    }


@router.get("/{task_id}")
def get_report_status(task_id: str, authorization: str = Header(None)):
    """
    查询报表生成状态（轮询接口）
    state: processing → done
    """
    _verify_token(authorization)

    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "msg": f"任务 {task_id} 不存在"},
        )
    return {"code": 200, "data": task}
