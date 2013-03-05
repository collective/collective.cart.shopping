from collective.cart.shopping.browser.viewlet import OrderConfirmationViewletManager

import unittest


class OrderConfirmationViewletManagerTestCase(unittest.TestCase):
    """TestCase for OrderConfirmationViewletManager"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewletManager
        self.assertTrue(issubclass(OrderConfirmationViewletManager, BaseViewletManager))

    def test_name(self):
        self.assertEqual(getattr(OrderConfirmationViewletManager, 'grokcore.component.directive.name'),
            'collective.cart.shopping.order.confirmation.manager')
