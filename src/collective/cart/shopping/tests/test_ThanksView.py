# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IThanksView
from collective.cart.shopping.browser.template import ThanksView
from collective.cart.shopping.tests.base import IntegrationTestCase


class ThanksViewTestCase(IntegrationTestCase):
    """TestCase for ThanksView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import CheckOutView
        self.assertTrue(issubclass(ThanksView, CheckOutView))
        from collective.cart.shopping.browser.interfaces import ICheckOutView
        self.assertTrue(issubclass(IThanksView, ICheckOutView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(ThanksView)
        self.assertTrue(verifyObject(IThanksView, instance))

    def test_template(self):
        instance = self.create_view(ThanksView)
        self.assertEqual(instance.template.filename.split('/')[-1], 'thanks.pt')
