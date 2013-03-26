from collective.cart.shopping.browser.viewlet import OrderConfirmationShippingMethodViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest

import mock


class OrderConfirmationShippingMethodViewletTestCase(IntegrationTestCase):
    """TestCase for OrderConfirmationShippingMethodViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseOrderConfirmationViewlet
        self.assertTrue(issubclass(OrderConfirmationShippingMethodViewlet, BaseOrderConfirmationViewlet))

    def test_name(self):
        self.assertEqual(getattr(OrderConfirmationShippingMethodViewlet, 'grokcore.component.directive.name'),
            'collective.cart.shopping.confirmation-shipping-method')

    def test_template(self):
        self.assertEqual(getattr(OrderConfirmationShippingMethodViewlet, 'grokcore.view.directive.template'),
            'confirmation-shipping-method')

    def create_viewlet(self):
        context = mock.Mock()
        request = TestRequest()
        return OrderConfirmationShippingMethodViewlet(context, request, None, None)

    @mock.patch('collective.cart.shopping.browser.viewlet.IAdapter')
    @mock.patch('collective.cart.shopping.browser.viewlet.IShoppingSite')
    def test_shipping_method(self, IShoppingSite, IAdapter):
        instance = self.create_viewlet()
        IShoppingSite().shipping_method = {'gross': self.money('12.40'), 'vat_rate': 24.0}
        IAdapter().percent.return_value = u'24%'
        self.assertEqual(instance.shipping_method, {
            'gross': self.money('12.40'),
            'is_free': False,
            'locale_gross': IShoppingSite().format_money(),
            'vat_rate': u'24%'
        })
