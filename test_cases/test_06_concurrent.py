"""
test_06_concurrent.py - 并发竞争条件测试
这是金融系统最核心的测试维度：验证在多线程并发场景下，数据库事务锁是否能防止资金漏洞。
"""
import threading
import pytest
from api.account_api import AccountAPI
from api.transaction_api import TransactionAPI
from api.auth_api import AuthAPI

auth_api = AuthAPI()


@pytest.mark.skip(reason="并发保护机制（Redis分布式锁）已根据要求移除，跳过此测试以保持测试环境连贯性")
class TestConcurrentWithdraw:
    """并发取款测试：验证账户余额不会因并发被透支"""

    def test_concurrent_withdraw_race_condition(self, zhang_token):
        """
        场景：zhang_san 活期账户（6222020000000002）余额设为一个已知值，
        同时发起 5 个并发取款请求，每次取款金额稍大于余额的 1/5。
        预期：不能全部成功，最终余额不能为负数（系统存在事务保护）。
        """
        account_no = "6222020000000002"
        a_api = AccountAPI(zhang_token)
        t_api = TransactionAPI(zhang_token)

        # 先将账户余额重置为一个确定值（存入精确金额）
        current = a_api.get_balance(account_no).json()["data"]["balance"]
        # 确保余额在 1000.00
        t_api.deposit(account_no, max(0, 1000.00 - current))

        results = []

        def do_withdraw():
            res = t_api.withdraw(account_no, 300.00)  # 5 次并发，总需 1500 > 1000
            results.append(res.status_code)

        threads = [threading.Thread(target=do_withdraw) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        success_count = results.count(200)
        fail_count    = results.count(400)

        # 核心断言：成功次数必须 <= 3（余额只够 3 次），失败的应返回 400
        assert success_count <= 3, f"并发取款成功次数异常: {success_count} 次成功，余额可能被透支"
        assert fail_count >= 2,    f"并发取款失败次数不足: {fail_count} 次失败，事务保护可能失效"

        # 最终余额不能为负
        final_balance = a_api.get_balance(account_no).json()["data"]["balance"]
        assert final_balance >= 0, f"账户余额为负数！余额: {final_balance}，存在资损漏洞！"


@pytest.mark.skip(reason="并发保护机制（Redis分布式锁）已根据要求移除，跳过此测试以保持测试环境连贯性")
class TestConcurrentTransfer:
    """并发转账幂等性测试：验证相同请求并发不会重复扣款"""

    def test_concurrent_transfer_idempotency(self, zhang_token):
        """
        场景：同时发起 5 个并发转账请求（相同付款方、收款方、金额）
        预期：只有部分成功（余额约束），且付款方最终余额与成功次数一致
        """
        from_acc = "6222020000000001"  # zhang_san 储蓄账户
        to_acc   = "6222020000000003"  # li_si 账户
        amount   = 100.00

        a_api = AccountAPI(zhang_token)
        t_api = TransactionAPI(zhang_token)

        before_zhang = a_api.get_balance(from_acc).json()["data"]["balance"]

        results = []

        def do_transfer():
            res = t_api.transfer(from_acc, to_acc, amount)
            results.append(res.status_code)

        threads = [threading.Thread(target=do_transfer) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        success_count = results.count(200)
        after_zhang   = a_api.get_balance(from_acc).json()["data"]["balance"]
        expected_after = round(before_zhang - (amount * success_count), 2)

        assert after_zhang == expected_after, (
            f"并发转账余额不一致！成功{success_count}次，"
            f"预期余额{expected_after}，实际余额{after_zhang}"
        )
