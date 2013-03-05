from collective.cart.shopping.browser.viewlet import BaseViewlet

import unittest


class BaseViewletTestCase(unittest.TestCase):
    """TestCase for BaseViewlet"""

    def test_subclass(self):
        from five.grok import Viewlet
        self.assertTrue(issubclass(BaseViewlet, Viewlet))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseViewlet, 'martian.martiandirective.baseclass'))

    def test_layer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        self.assertEqual(getattr(BaseViewlet, 'grokcore.view.directive.layer'), ICollectiveCartShoppingLayer)

    def test_require(self):
        self.assertEqual(getattr(BaseViewlet, 'grokcore.security.directive.require'), ['zope2.View'])
