from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# ================= 数据库配置区 =================
DB_CONFIG = {
    'host': '192.168.152.1',
    'user': 'root',
    'password': '123456789Yj',  # ⚠️ 长官，请修改为你的 MySQL 密码！
    'database': 'mall_target',
    'cursorclass': pymysql.cursors.DictCursor
}


def get_db():
    return pymysql.connect(**DB_CONFIG)


# ================= API 1：账号登录 =================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        # 登录成功，下发专属 Token
        return jsonify({"code": 200, "msg": "登录成功", "token": f"VIP_TOKEN_{user['id']}"})
    else:
        return jsonify({"code": 401, "msg": "账号或密码错误"})


# ================= API 2：创建订单 =================
@app.route('/api/order/create', methods=['POST'])
def create_order():
    token = request.headers.get('token')
    if not token or not token.startswith('VIP_TOKEN_'):
        return jsonify({"code": 403, "msg": "未授权，请提供有效Token"})

    user_id = token.split('_')[-1]
    data = request.json

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, product_name, amount, status) VALUES (%s, %s, %s, 0)",
                   (user_id, data.get('product_name'), data.get('amount')))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()

    return jsonify({"code": 200, "msg": "下单成功", "order_id": order_id})


# ================= API 3：支付扣款 =================
@app.route('/api/order/pay', methods=['POST'])
def pay_order():
    token = request.headers.get('token')
    if not token:
        return jsonify({"code": 403, "msg": "未授权"})

    user_id = token.split('_')[-1]
    order_id = request.json.get('order_id')

    conn = get_db()
    cursor = conn.cursor()

    # 1. 查订单是否存在
    cursor.execute("SELECT * FROM orders WHERE id=%s AND user_id=%s", (order_id, user_id))
    order = cursor.fetchone()
    if not order:
        conn.close()
        return jsonify({"code": 404, "msg": "订单不存在"})

    if order['status'] == 1:
        conn.close()
        return jsonify({"code": 400, "msg": "订单已支付，请勿重复扣款"})

    # 2. 查余额是否充足
    cursor.execute("SELECT balance FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if user['balance'] < order['amount']:
        conn.close()
        return jsonify({"code": 400, "msg": "余额不足，支付失败"})

    # 3. 核心交易事务：扣钱 + 改订单状态
    try:
        cursor.execute("UPDATE users SET balance = balance - %s WHERE id=%s", (order['amount'], user_id))
        cursor.execute("UPDATE orders SET status = 1 WHERE id=%s", (order_id,))
        conn.commit()
        res = {"code": 200, "msg": "支付成功"}
    except Exception as e:
        conn.rollback()
        res = {"code": 500, "msg": "支付异常"}
    finally:
        conn.close()

    return jsonify(res)


if __name__ == '__main__':
    print("🚀 报告长官！电商靶机已启动，正在监听 5000 端口...")
    app.run(port=5000, debug=True)