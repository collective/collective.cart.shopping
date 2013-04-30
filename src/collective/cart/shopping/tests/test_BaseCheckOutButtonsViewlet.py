# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IBaseCheckOutButtonsViewlet
from collective.cart.shopping.browser.viewlet import BaseCheckOutButtonsViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class BaseCheckOutButtonsViewletTestCase(IntegrationTestCase):
    """TestCase for BaseCheckOutButtonsViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(BaseCheckOutButtonsViewlet, ViewletBase))
        from collective.base.interfaces import IViewlet
        self.assertTrue(issubclass(IBaseCheckOutButtonsViewlet, IViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(BaseCheckOutButtonsViewlet)
        self.assertTrue(verifyObject(IBaseCheckOutButtonsViewlet, instance))

    def test_update(self):
        from zExceptions import Forbidden
        instance = self.create_viewlet(BaseCheckOutButtonsViewlet)
        instance.context.restrictedTraverse = mock.Mock()
        instance.context.restrictedTraverse().verify.return_value = False

        instance.request.form = {'form.buttons.CheckOut': True}
        with self.assertRaises(Forbidden):
            instance.update()

        instance.request.form = {'form.buttons.Back': True}
        with self.assertRaises(Forbidden):
            instance.update()
