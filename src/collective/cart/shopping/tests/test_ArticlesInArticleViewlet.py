# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IArticlesInArticleViewlet
from collective.cart.shopping.browser.viewlet import ArticlesInArticleViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class ArticlesInArticleViewletTestCase(IntegrationTestCase):
    """TestCase for ArticlesInArticleViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import AddToCartViewlet
        self.assertTrue(issubclass(ArticlesInArticleViewlet, AddToCartViewlet))
        from collective.cart.shopping.browser.interfaces import IAddToCartViewlet
        self.assertTrue(issubclass(IArticlesInArticleViewlet, IAddToCartViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(ArticlesInArticleViewlet)
        self.assertTrue(verifyObject(IArticlesInArticleViewlet, instance))
