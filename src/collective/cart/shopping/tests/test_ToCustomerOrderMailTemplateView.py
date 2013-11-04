# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IToCustomerOrderMailTemplateView
from collective.cart.shopping.browser.view import ToCustomerOrderMailTemplateView
from collective.cart.shopping.tests.base import IntegrationTestCase


class ToCustomerOrderMailTemplateViewTestCase(IntegrationTestCase):
    """TestCase for ToCustomerOrderMailTemplateView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.view import BaseOrderMailTemplateView
        self.assertTrue(issubclass(ToCustomerOrderMailTemplateView, BaseOrderMailTemplateView))
        from collective.cart.shopping.browser.interfaces import IBaseOrderMailTemplateView
        self.assertTrue(issubclass(IToCustomerOrderMailTemplateView, IBaseOrderMailTemplateView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(ToCustomerOrderMailTemplateView)
        self.assertTrue(verifyObject(IToCustomerOrderMailTemplateView, instance))
