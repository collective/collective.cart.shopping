from collective.cart.shopping.browser.viewlet import ArticleContainerViewletManager

import unittest


class ArticleContainerViewletManagerTestCase(unittest.TestCase):
    """TestCase for ArticleContainerViewletManager"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewletManager
        self.assertTrue(issubclass(ArticleContainerViewletManager, BaseViewletManager))

    def test_context(self):
        from collective.cart.shopping.interfaces import IArticleContainer
        self.assertTrue(getattr(ArticleContainerViewletManager, 'grokcore.component.directive.context'), IArticleContainer)

    def test_name(self):
        self.assertTrue(getattr(ArticleContainerViewletManager, 'grokcore.component.directive.name'),
            'collective.cart.shopping.articlecontainer')
