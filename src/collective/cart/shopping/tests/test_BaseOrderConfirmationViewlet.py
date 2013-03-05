from collective.cart.shopping.browser.viewlet import BaseOrderConfirmationViewlet

import unittest


class BaseOrderConfirmationViewletTestCase(unittest.TestCase):
    """TestCase for BaseOrderConfirmationViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseShoppingSiteRootViewlet
        self.assertTrue(issubclass(BaseOrderConfirmationViewlet, BaseShoppingSiteRootViewlet))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseOrderConfirmationViewlet, 'martian.martiandirective.baseclass'))

    def test_viewletmanager(self):
        from collective.cart.shopping.browser.viewlet import OrderConfirmationViewletManager
        self.assertEqual(getattr(BaseOrderConfirmationViewlet, 'grokcore.viewlet.directive.viewletmanager'),
            OrderConfirmationViewletManager)
