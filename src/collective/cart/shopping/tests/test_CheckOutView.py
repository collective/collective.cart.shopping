# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import ICheckOutView
from collective.cart.shopping.browser.template import CheckOutView
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class CheckOutViewTestCase(IntegrationTestCase):
    """TestCase for CheckOutView"""

    def test_subclass(self):
        from collective.cart.core.browser.template import CheckOutView as BaseCheckOutView
        from collective.cart.shopping.browser.base import Message
        self.assertTrue(issubclass(CheckOutView, (BaseCheckOutView, Message)))
        from collective.cart.core.browser.interfaces import ICheckOutView as IBaseCheckOutView
        self.assertTrue(issubclass(ICheckOutView, IBaseCheckOutView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(CheckOutView)
        self.assertTrue(verifyObject(ICheckOutView, instance))

    def test_description(self):
        instance = self.create_view(CheckOutView)
        instance.message = mock.Mock(return_value={})
        self.assertIsNone(instance.description())

        instance.message= mock.Mock(return_value={'description': 'DESCRIPTION'})
        self.assertEqual(instance.description(), 'DESCRIPTION')
