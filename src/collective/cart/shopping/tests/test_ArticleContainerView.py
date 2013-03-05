from collective.cart.shopping.browser.template import ArticleContainerView

import unittest


class ArticleContainerViewTestCase(unittest.TestCase):
    """TestCase for ArticleContainerView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseView
        self.assertTrue(issubclass(ArticleContainerView, BaseView))

    def test_context(self):
        from collective.cart.shopping.interfaces import IArticleContainer
        self.assertTrue(getattr(ArticleContainerView, 'grokcore.component.directive.context'), IArticleContainer)

    def test_name(self):
        self.assertTrue(getattr(ArticleContainerView, 'grokcore.component.directive.name'), 'view')

    def test_template(self):
        self.assertTrue(getattr(ArticleContainerView, 'grokcore.view.directive.template'), 'article-container')
