import os

# 银行服务地址（本地默认 8000，Docker 环境通过环境变量覆盖）
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")

# 认证模块
REGISTER_URL       = f"{BASE_URL}/api/auth/register"
LOGIN_URL          = f"{BASE_URL}/api/auth/login"

# 账户模块
CREATE_ACCOUNT_URL = f"{BASE_URL}/api/account/create"
ACCOUNT_DETAIL_URL = f"{BASE_URL}/api/account"        # + /{account_no}
BALANCE_URL        = f"{BASE_URL}/api/account/balance" # + /{account_no}
CLOSE_ACCOUNT_URL  = f"{BASE_URL}/api/account/close"   # + /{account_no}

# 交易模块
DEPOSIT_URL        = f"{BASE_URL}/api/transaction/deposit"
WITHDRAW_URL       = f"{BASE_URL}/api/transaction/withdraw"
TRANSFER_URL       = f"{BASE_URL}/api/transaction/transfer"
CROSS_TRANSFER_URL = f"{BASE_URL}/api/transaction/transfer/cross-bank"
HISTORY_URL        = f"{BASE_URL}/api/transaction/history"
