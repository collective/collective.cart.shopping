from collective.cart.shopping.browser.viewlet import BaseArticleViewlet

import unittest


class BaseArticleViewletTestCase(unittest.TestCase):
    """TestCase for BaseArticleViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewlet
        self.assertTrue(issubclass(BaseArticleViewlet, BaseViewlet))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseArticleViewlet, 'martian.martiandirective.baseclass'))

    def test_context(self):
        from collective.cart.shopping.interfaces import IArticle
        self.assertTrue(getattr(BaseArticleViewlet, 'grokcore.component.directive.context'), IArticle)
