# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IArticleView
from collective.cart.shopping.browser.template import ArticleView
from collective.cart.shopping.tests.base import IntegrationTestCase


class ArticleViewTestCase(IntegrationTestCase):
    """TestCase for ArticleView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseArticleView
        self.assertTrue(issubclass(ArticleView, BaseArticleView))
        from collective.cart.shopping.browser.interfaces import IBaseArticleView
        self.assertTrue(issubclass(IArticleView, IBaseArticleView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article', title="Ärticle")
        instance = self.create_view(ArticleView, context)
        self.assertTrue(verifyObject(IArticleView, instance))
