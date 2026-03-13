import pytest
import allure
from utils import * #为什么没用
from api.order_api import OrderAPI
from utils.yaml_util import read_yaml
from utils.db_util import db
from utils.logger import log


@allure.epic("电商核心链路测试")
@allure.feature("订单支付模块")
class TestOrderPay:

    @allure.story("异常支付-余额不足")
    @allure.title("测试: 购买 {case_data[product_name]} 余额不足拦截")
    @pytest.mark.parametrize("case_data", read_yaml("test_data.yaml")["pay_fail_data"])
    def test_pay_fail_ultimate(self, get_token, order_cleaner, case_data):
        log.info("========== 测试用例开始执行 ==========")
        order_api = OrderAPI(get_token)  # 实例化 API 操作对象 这句怎么理解

        with allure.step("1. 拍快照：记录初始余额"):
            initial_balance = db.query_one("SELECT balance FROM users WHERE username = 'kobe'")["balance"]
            log.info(f"战前快照: 余额={initial_balance}")
            #怎么样会产生bug日志呢

        with allure.step("2. 执行业务：创建订单"):
            res_create = order_api.create_order(case_data["product_name"], case_data["amount"])
            order_id = res_create.json()["order_id"]
            order_cleaner.append(order_id)  # 扔进垃圾筐防爆

        with allure.step("3. 执行业务：发起支付"):
            res_pay = order_api.pay_order(order_id)

        with allure.step("4. 接口与数据库物理断言"):
            assert res_pay.json()["code"] == case_data["expect_code"]
            assert case_data["expect_msg"] in res_pay.json()["msg"]

            # DB校验
            order_status = db.query_one(f"SELECT status FROM orders WHERE id = {order_id}")
            current_balance = db.query_one("SELECT balance FROM users WHERE username = 'kobe'")["balance"]
            assert order_status['status'] == 0, f'订单状态异常'
            assert current_balance == initial_balance, "⚠️ 发生资损！"
            log.info("========== 测试用例执行成功 ==========\n")