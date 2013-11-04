# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IBillingAndShippingView
from collective.cart.shopping.browser.view import BillingAndShippingView
from collective.cart.shopping.tests.base import IntegrationTestCase


class BillingAndShippingViewTestCase(IntegrationTestCase):
    """TestCase for BillingAndShippingView"""

    def test_issubclass(self):
        from collective.cart.shopping.browser.view import CheckOutView
        self.assertTrue(issubclass(BillingAndShippingView, CheckOutView))
        from collective.cart.shopping.browser.interfaces import ICheckOutView
        self.assertTrue(issubclass(IBillingAndShippingView, ICheckOutView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(BillingAndShippingView)
        self.assertTrue(verifyObject(IBillingAndShippingView, instance))
