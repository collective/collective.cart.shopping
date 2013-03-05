from collective.cart.shopping.browser.viewlet import BelowArticleViewletManager

import unittest


class AddToCartViewletManagetTestCase(unittest.TestCase):
    """TestCase for BelowArticleViewletManager"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewletManager
        self.assertTrue(issubclass(BelowArticleViewletManager, BaseViewletManager))

    def test_context(self):
        from collective.cart.shopping.interfaces import IArticle
        self.assertTrue(getattr(BelowArticleViewletManager, 'grokcore.component.directive.context'), IArticle)

    def test_name(self):
        self.assertTrue(getattr(BelowArticleViewletManager, 'grokcore.component.directive.name'), 'collective.cart.shopping.below.article')
