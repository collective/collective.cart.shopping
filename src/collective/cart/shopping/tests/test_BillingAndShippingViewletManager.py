from collective.cart.shopping.browser.viewlet import BillingAndShippingViewletManager

import unittest


class BillingAndShippingViewletManagerTestCase(unittest.TestCase):
    """TestCase for BillingAndShippingViewletManager"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewletManager
        self.assertTrue(issubclass(BillingAndShippingViewletManager, BaseViewletManager))

    def test_name(self):
        self.assertTrue(getattr(BillingAndShippingViewletManager, 'grokcore.component.directive.name'),
            'collective.cart.shopping.billing.shipping.manager')
