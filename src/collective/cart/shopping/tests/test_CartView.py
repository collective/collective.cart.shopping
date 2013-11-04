# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import ICartView
from collective.cart.shopping.browser.view import CartView
from collective.cart.shopping.tests.base import IntegrationTestCase


class CartViewTestCase(IntegrationTestCase):
    """TestCase for CartView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.view import CheckOutView
        self.assertTrue(issubclass(CartView, CheckOutView))
        from collective.cart.shopping.browser.interfaces import ICheckOutView
        self.assertTrue(issubclass(ICartView, ICheckOutView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(CartView)
        self.assertTrue(verifyObject(ICartView, instance))
