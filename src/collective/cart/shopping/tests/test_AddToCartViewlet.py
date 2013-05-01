# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IAddToCartViewlet
from collective.cart.shopping.browser.viewlet import AddToCartViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class AddToCartViewletTestCase(IntegrationTestCase):
    """TestCase for AddToCartViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseAddToCartViewlet
        self.assertTrue(issubclass(AddToCartViewlet, BaseAddToCartViewlet))
        from collective.cart.shopping.browser.interfaces import IBaseAddToCartViewlet
        self.assertTrue(issubclass(IAddToCartViewlet, IBaseAddToCartViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(AddToCartViewlet, context)
        self.assertTrue(verifyObject(IAddToCartViewlet, instance))
