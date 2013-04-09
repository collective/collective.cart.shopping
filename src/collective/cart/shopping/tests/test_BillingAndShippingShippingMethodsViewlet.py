from collective.cart.shopping.browser.viewlet import BillingAndShippingShippingMethodsViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest

import mock


class BillingAndShippingShippingMethodsViewletTestCase(IntegrationTestCase):
    """TestCase for BillingAndShippingShippingMethodsViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseShoppingSiteRootViewlet
        self.assertTrue(issubclass(BillingAndShippingShippingMethodsViewlet, BaseShoppingSiteRootViewlet))

    def test_name(self):
        self.assertEqual(getattr(BillingAndShippingShippingMethodsViewlet, 'grokcore.component.directive.name'), 'collective.cart.shopping.billing-and-shipping-shipping-methods')

    def test_template(self):
        self.assertTrue(getattr(BillingAndShippingShippingMethodsViewlet, 'grokcore.view.directive.template'), 'billing-and-shipping-shipping-methods')

    def test_viewletmanager(self):
        from collective.cart.shopping.browser.viewlet import BillingAndShippingViewletManager
        self.assertEqual(getattr(BillingAndShippingShippingMethodsViewlet, 'grokcore.viewlet.directive.viewletmanager'), BillingAndShippingViewletManager)

    @mock.patch('collective.cart.shopping.browser.viewlet.BillingAndShippingShippingMethodsViewlet.single_shipping_method', new_callable=mock.PropertyMock)
    def test_update(self, single_shipping_method):
        instance = self.create_viewlet(BillingAndShippingShippingMethodsViewlet)
        instance.request.form = {'form.to.confirmation': True}
        single_shipping_method.return_value = False
        instance.update()
        self.assertEqual(instance.message, u'Select one shipping method.')
