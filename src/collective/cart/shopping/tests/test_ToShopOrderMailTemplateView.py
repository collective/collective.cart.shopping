# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IToShopOrderMailTemplateView
from collective.cart.shopping.browser.template import ToShopOrderMailTemplateView
from collective.cart.shopping.tests.base import IntegrationTestCase


class ToShopOrderMailTemplateViewTestCase(IntegrationTestCase):
    """TestCase for ToShopOrderMailTemplateView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseOrderMailTemplateView
        self.assertTrue(issubclass(ToShopOrderMailTemplateView, BaseOrderMailTemplateView))
        from collective.cart.shopping.browser.interfaces import IBaseOrderMailTemplateView
        self.assertTrue(issubclass(IToShopOrderMailTemplateView, IBaseOrderMailTemplateView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(ToShopOrderMailTemplateView)
        self.assertTrue(verifyObject(IToShopOrderMailTemplateView, instance))