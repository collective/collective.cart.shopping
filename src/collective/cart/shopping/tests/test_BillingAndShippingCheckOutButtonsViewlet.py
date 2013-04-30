# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IBillingAndShippingCheckOutButtonsViewlet
from collective.cart.shopping.browser.viewlet import BillingAndShippingCheckOutButtonsViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class BillingAndShippingCheckOutButtonsViewletTestCase(IntegrationTestCase):
    """TestCase for BillingAndShippingCheckOutButtonsViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCheckOutButtonsViewlet
        self.assertTrue(issubclass(BillingAndShippingCheckOutButtonsViewlet, BaseCheckOutButtonsViewlet))
        from collective.cart.shopping.browser.interfaces import IBaseCheckOutButtonsViewlet
        self.assertTrue(issubclass(IBillingAndShippingCheckOutButtonsViewlet, IBaseCheckOutButtonsViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(BillingAndShippingCheckOutButtonsViewlet)
        self.assertTrue(verifyObject(IBillingAndShippingCheckOutButtonsViewlet, instance))

    @mock.patch('collective.cart.shopping.browser.viewlet.IStatusMessage')
    @mock.patch('collective.cart.shopping.browser.viewlet.BaseCheckOutButtonsViewlet.update', mock.Mock(return_value='URL'))
    def test_update(self, IStatusMessage):
        from collective.cart.shopping.browser.template import BillingAndShippingView
        view = self.create_view(BillingAndShippingView)
        instance = self.create_viewlet(BillingAndShippingCheckOutButtonsViewlet, view=view)
        instance.context.restrictedTraverse = mock.Mock()
        instance.context.restrictedTraverse().current_base_url.return_value = 'CURRENT_BASE_URL'
        instance.request.form = {'form.buttons.CheckOut': True}
        instance.single_shipping_method = mock.Mock(return_value=False)
        self.assertEqual(instance.update(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u'Select one shipping method.', type='warn')
