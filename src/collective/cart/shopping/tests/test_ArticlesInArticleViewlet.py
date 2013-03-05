from collective.cart.shopping.browser.viewlet import ArticlesInArticleViewlet

import unittest


class ArticlesInArticleViewletTestCase(unittest.TestCase):
    """TestCase for ArticlesInArticleViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseArticleViewlet
        self.assertTrue(issubclass(ArticlesInArticleViewlet, BaseArticleViewlet))

    def test_name(self):
        self.assertEqual(getattr(ArticlesInArticleViewlet, 'grokcore.component.directive.name'), 'collective.cart.shopping.articles.in.article')

    def test_template(self):
        self.assertEqual(getattr(ArticlesInArticleViewlet, 'grokcore.view.directive.template'), 'articles-in-article')

    def test_viewletmanager(self):
        from collective.cart.shopping.browser.viewlet import BelowArticleViewletManager
        self.assertEqual(getattr(ArticlesInArticleViewlet, 'grokcore.viewlet.directive.viewletmanager'), BelowArticleViewletManager)
