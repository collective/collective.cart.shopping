# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IOrderConfirmationView
from collective.cart.shopping.browser.view import OrderConfirmationView
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class OrderConfirmationViewTestCase(IntegrationTestCase):
    """TestCase for OrderConfirmationView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.view import CheckOutView
        self.assertTrue(issubclass(OrderConfirmationView, CheckOutView))
        from collective.cart.shopping.browser.interfaces import ICheckOutView
        self.assertTrue(issubclass(IOrderConfirmationView, ICheckOutView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(OrderConfirmationView)
        self.assertTrue(verifyObject(IOrderConfirmationView, instance))

    @mock.patch('collective.cart.shopping.browser.view.CheckOutView.__call__')
    @mock.patch('collective.cart.shopping.browser.view.IStatusMessage')
    def test___call__(self, IStatusMessage, __call__):
        instance = self.create_view(OrderConfirmationView)
        instance.context.absolute_url = mock.Mock(return_value='URL')
        self.assertEqual(instance(), 'URL/@@billing-and-shipping')
        IStatusMessage().addStatusMessage.assert_called_with(u'info_missing_from_addresses', type='info')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 1)
        self.assertEqual(__call__.call_count, 0)

        instance.shopping_site = mock.Mock()
        self.assertIsNone(instance())

        __call__.return_value = None
        instance.template = mock.Mock(return_value='TEMPLATE')
        self.assertEqual(instance(), 'TEMPLATE')
