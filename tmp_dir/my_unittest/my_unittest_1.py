from unittest import mock
import unittest

import temple
from temple import MYA


class TestZhifuStatues(unittest.TestCase):
    """单元测试用例"""

    @mock.patch("temple.zhifu")
    def test_01(self, mock_zhifu):
        """测试支付成功场景"""
        # 方法一：mock一个支付成功的数据
        # temple.zhifu = mock.Mock(return_value={"result": "success", "reason":"null"})

        # 方法二：mock.path装饰器模拟返回结果
        mock_zhifu.return_value = {"result": "success", "reason": "null"}
        # 根据支付结果测试页面跳转
        statues = temple.zhifu_statues()
        print(statues)
        self.assertEqual(statues, "支付成功")

    @mock.patch("temple.zhifu")
    def test_02(self, mock_zhifu):
        """测试支付失败场景"""
        # mock一个支付成功的数据

        mock_zhifu.return_value = {"result": "fail", "reason": "余额不足"}
        # 根据支付结果测试页面跳转
        statues = temple.zhifu_statues()
        self.assertEqual(statues, "支付失败")

    @mock.patch.object(MYA, 'foo_1')
    def test_03(self, mock_foo_1):
        mock_foo_1.return_value = 10
        data = MYA.foo_4('_', '_')
        print(data)
        self.assertEqual(data, 5)


if __name__ == "__main__":
    unittest.main()

