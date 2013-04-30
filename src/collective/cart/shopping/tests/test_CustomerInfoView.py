# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import ICustomerInfoView
from collective.cart.shopping.browser.template import CustomerInfoView
from collective.cart.shopping.tests.base import IntegrationTestCase


class CustomerInfoViewTestCase(IntegrationTestCase):
    """TestCase for CustomerInfoView"""

    def test_subclass(self):
        from Products.Five.browser import BrowserView
        self.assertTrue(issubclass(CustomerInfoView, BrowserView))
        from plone.app.layout.globals.interfaces import IViewView
        self.assertTrue(issubclass(ICustomerInfoView, IViewView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(CustomerInfoView)
        self.assertTrue(verifyObject(ICustomerInfoView, instance))

    def test___call__(self):
        instance = self.create_view(CustomerInfoView)
        self.assertEqual(instance.__call__.filename.split('/')[-1], 'customer-info.pt')
