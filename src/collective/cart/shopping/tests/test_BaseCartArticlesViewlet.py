from collective.cart.shopping.browser.viewlet import BaseCartArticlesViewlet

import unittest


class BaseCartArticlesViewletTestCase(unittest.TestCase):
    """TestCase for BaseCartArticlesViewlet"""

    def test_subclass(self):
        from collective.cart.core.browser.viewlet import CartArticlesViewlet
        self.assertTrue(issubclass(BaseCartArticlesViewlet, CartArticlesViewlet))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseCartArticlesViewlet, 'martian.martiandirective.baseclass'))

    def test_layer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        self.assertEqual(getattr(BaseCartArticlesViewlet, 'grokcore.view.directive.layer'), ICollectiveCartShoppingLayer)
