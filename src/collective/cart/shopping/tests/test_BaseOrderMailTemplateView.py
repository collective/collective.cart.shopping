# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IBaseOrderMailTemplateView
from collective.cart.shopping.browser.template import BaseOrderMailTemplateView
from collective.cart.shopping.tests.base import IntegrationTestCase


class BaseOrderMailTemplateViewTestCase(IntegrationTestCase):
    """TestCase for BaseOrderMailTemplateView"""

    def test_subclass(self):
        from Products.Five.browser import BrowserView
        self.assertTrue(issubclass(BaseOrderMailTemplateView, BrowserView))
        from collective.cart.shopping.browser.interfaces import IViewView
        self.assertTrue(issubclass(IBaseOrderMailTemplateView, IViewView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(BaseOrderMailTemplateView)
        self.assertTrue(verifyObject(IBaseOrderMailTemplateView, instance))