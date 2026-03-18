"""
Pydantic 请求/响应数据模型定义
FastAPI 会自动用这些模型做请求体验证，并生成 Swagger 文档
"""
from pydantic import BaseModel, Field
from typing import Optional


# ==================== 用户认证模块 ====================

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="zhang_san")
    password: str = Field(..., min_length=8, max_length=50, example="Test@1234")
    phone:    str = Field(..., min_length=11, max_length=11, example="13800138001")


class LoginRequest(BaseModel):
    username: str = Field(..., example="zhang_san")
    password: str = Field(..., example="Test@1234")


# ==================== 账户模块 ====================

class CreateAccountRequest(BaseModel):
    account_type: str = Field(default="savings", example="savings",
                              description="账户类型: savings=储蓄账户, current=活期账户")


# ==================== 存取款模块 ====================

class DepositRequest(BaseModel):
    account_no: str   = Field(..., example="6222020000000001")
    amount:     float = Field(..., gt=0, le=500000, example=1000.00,
                              description="存款金额，单位：元，单笔上限 50 万")


class WithdrawRequest(BaseModel):
    account_no: str   = Field(..., example="6222020000000001")
    amount:     float = Field(..., gt=0, le=50000, example=500.00,
                              description="取款金额，单位：元，单笔上限 5 万")


# ==================== 转账模块 ====================

class TransferRequest(BaseModel):
    from_account: str            = Field(..., example="6222020000000001", description="付款账号")
    to_account:   str            = Field(..., example="6222020000000003", description="收款账号")
    amount:       float          = Field(..., gt=0, example=1000.00, description="转账金额（元）")
    remark:       Optional[str]  = Field(default=None, example="还款", description="转账备注（选填）")


class CrossBankTransferRequest(BaseModel):
    from_account: str   = Field(..., example="6222020000000001")
    to_bank_code: str   = Field(..., example="ICBC", description="收款行代码: ICBC/ABC/BOC/CCB")
    to_account:   str   = Field(..., example="6221001234567890")
    amount:       float = Field(..., gt=0, example=2000.00)
