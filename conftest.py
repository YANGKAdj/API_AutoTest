import pytest
import requests
from utils.db_util import db

#全局夹具
# scope="session" 意味着：不管跑多少个用例，登录只在最开始执行一次，极致节省时间！
@pytest.fixture(scope="session")
def get_token():
    print("\n[全局后勤] 📡 正在向靶机申请全局通行证...")
    url = "http://127.0.0.1:5000/api/login"
    payload = {"username": "kobe", "password": "123456"}

    res = requests.post(url, json=payload)
    token = res.json().get("token")
    print(f"[全局后勤] ✅ 通行证下发成功: {token}")
    return token


@pytest.fixture
def order_cleaner():
    # 1. yield 前面是【准备阶段】：我们准备一个空的“垃圾筐”
    trash_bin = []

    # 2. 极其关键的 yield！它会把这个空筐子递给前线的测试用例，然后在此处挂起等待！
    yield trash_bin

    # 3. yield 后面是【强制清场阶段】：一旦测试用例运行结束（不管它是绿灯还是红灯报错），
    # Pytest 都会强制回到这里，执行下面的代码！
    print("\n[神级后勤] 🧹 检测到演习结束，启动绝对防御清场程序...")
    for order_id in trash_bin:
        db.execute(f"DELETE FROM orders WHERE id = {order_id}")
        print(f"[神级后勤] 🗑️ 战争孤儿(订单 {order_id})已被无情抹杀！")