# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IBaseAddToCartViewlet
from collective.cart.shopping.browser.viewlet import BaseAddToCartViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class BaseAddToCartViewletTestCase(IntegrationTestCase):
    """TestCase for BaseAddToCartViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseArticleViewlet
        from collective.cart.core.browser.viewlet import AddToCartViewlet
        self.assertTrue(issubclass(BaseAddToCartViewlet, (BaseArticleViewlet, AddToCartViewlet)))
        from collective.cart.shopping.browser.interfaces import IBaseArticleViewlet
        from collective.cart.shopping.browser.interfaces import IAddToCartViewlet
        self.assertTrue(issubclass(IBaseAddToCartViewlet, (IBaseArticleViewlet, IAddToCartViewlet)))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.shopping.ArticleContainer')
        instance = self.create_viewlet(BaseAddToCartViewlet, context)
        self.assertTrue(verifyObject(IBaseAddToCartViewlet, instance))
