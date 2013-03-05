from collective.cart.shopping.browser.viewlet import AddToCartViewletManager

import unittest


class AddToCartViewletManagerTestCase(unittest.TestCase):
    """TestCase for AddToCartViewletManager"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewletManager
        self.assertTrue(issubclass(AddToCartViewletManager, BaseViewletManager))

    def test_context(self):
        from collective.cart.shopping.interfaces import IArticle
        self.assertTrue(getattr(AddToCartViewletManager, 'grokcore.component.directive.context'), IArticle)

    def test_name(self):
        self.assertTrue(getattr(AddToCartViewletManager, 'grokcore.component.directive.name'), 'collective.cart.shopping.add.to.cart.manager')
