# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import ICartCheckOutButtonsViewlet
from collective.cart.shopping.browser.viewlet import CartCheckOutButtonsViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class CartCheckOutButtonsViewletTestCase(IntegrationTestCase):
    """TestCase for CartCheckOutButtonsViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCheckOutButtonsViewlet
        self.assertTrue(issubclass(CartCheckOutButtonsViewlet, BaseCheckOutButtonsViewlet))
        from collective.cart.shopping.browser.interfaces import IBaseCheckOutButtonsViewlet
        self.assertTrue(issubclass(ICartCheckOutButtonsViewlet, IBaseCheckOutButtonsViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(CartCheckOutButtonsViewlet)
        self.assertTrue(verifyObject(ICartCheckOutButtonsViewlet, instance))

    def test_update(self):
        from zExceptions import Forbidden
        instance = self.create_viewlet(CartCheckOutButtonsViewlet)
        instance.context.restrictedTraverse = mock.Mock()
        instance.context.restrictedTraverse().verify.return_value = False
        instance.request.form = {'form.buttons.ClearCart': True}
        with self.assertRaises(Forbidden):
            instance.update()
