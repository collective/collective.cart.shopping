from collective.cart.shopping.browser.viewlet import BaseCartViewlet

import unittest


class BaseCartViewletTestCase(unittest.TestCase):
    """TestCase for BaseCartViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseShoppingSiteRootViewlet
        self.assertTrue(issubclass(BaseCartViewlet, BaseShoppingSiteRootViewlet))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseCartViewlet, 'martian.martiandirective.baseclass'))

    def test_viewletmanager(self):
        from collective.cart.shopping.browser.viewlet import CartViewletManager
        self.assertEqual(getattr(BaseCartViewlet, 'grokcore.viewlet.directive.viewletmanager'), CartViewletManager)
