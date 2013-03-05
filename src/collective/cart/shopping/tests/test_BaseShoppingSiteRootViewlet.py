from collective.cart.shopping.browser.viewlet import BaseShoppingSiteRootViewlet

import unittest


class BaseShoppingSiteRootViewletTestCase(unittest.TestCase):
    """TestCase for BaseShoppingSiteRootViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewlet
        self.assertTrue(issubclass(BaseShoppingSiteRootViewlet, BaseViewlet))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseShoppingSiteRootViewlet, 'martian.martiandirective.baseclass'))

    def test_context(self):
        from collective.cart.core.interfaces import IShoppingSiteRoot
        self.assertTrue(getattr(BaseShoppingSiteRootViewlet, 'grokcore.component.directive.context'), IShoppingSiteRoot)
