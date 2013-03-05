from collective.cart.shopping.browser.template import BillingAndShippingView

import unittest


class BillingAndShippingViewTestCase(unittest.TestCase):
    """TestCase for BillingAndShippingView"""

    def test_name(self):
        self.assertTrue(getattr(BillingAndShippingView, 'grokcore.component.directive.name'), 'billing-and-shipping')

    def test_template(self):
        self.assertTrue(getattr(BillingAndShippingView, 'grokcore.view.directive.template'), 'billing-and-shipping')

    def test_issubclass(self):
        from collective.cart.shopping.browser.template import BaseCheckOutView
        from collective.cart.shopping.browser.base import Message
        self.assertTrue(issubclass(BillingAndShippingView, (BaseCheckOutView, Message)))
