# from collective.cart.shopping.browser.viewlet import OrderConfirmationTotalViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class OrderConfirmationTotalViewletTestCase(IntegrationTestCase):
    """TestCase for OrderConfirmationTotalViewlet"""

    def test(self):
        pass

    # def test_subclass(self):
    #     from collective.cart.shopping.browser.viewlet import BaseOrderConfirmationViewlet
    #     self.assertTrue(issubclass(OrderConfirmationTotalViewlet, BaseOrderConfirmationViewlet))

    # def test_name(self):
    #     self.assertEqual(getattr(OrderConfirmationTotalViewlet, 'grokcore.component.directive.name'),
    #         'collective.cart.shopping.confirmation-total')

    # def test_template(self):
    #     self.assertEqual(getattr(OrderConfirmationTotalViewlet, 'grokcore.view.directive.template'),
    #         'confirmation-total')

    # def create_viewlet(self):
    #     context = mock.Mock()
    #     request = TestRequest()
    #     return OrderConfirmationTotalViewlet(context, request, None, None)

    # @mock.patch('collective.cart.shopping.browser.viewlet.IShoppingSite')
    # def test_total(self, IShoppingSite):
    #     instance = self.create_viewlet()
    #     self.assertEqual(instance.total(), IShoppingSite().locale_total())
