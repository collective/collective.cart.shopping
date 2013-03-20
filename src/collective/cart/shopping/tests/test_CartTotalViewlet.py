from collective.cart.shopping.browser.viewlet import CartTotalViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest

import mock


class CartTotalViewletTestCase(IntegrationTestCase):
    """TestCase for CartTotalViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCartViewlet
        self.assertTrue(issubclass(CartTotalViewlet, BaseCartViewlet))

    def test_name(self):
        self.assertEqual(getattr(CartTotalViewlet, 'grokcore.component.directive.name'), 'collective.cart.shopping.cart-total')

    def test_template(self):
        self.assertTrue(getattr(CartTotalViewlet, 'grokcore.view.directive.template'), 'cart-total')

    def create_viewlet(self):
        context = mock.Mock()
        request = TestRequest()
        return CartTotalViewlet(context, request, None, None)

    @mock.patch('collective.cart.shopping.browser.viewlet.IShoppingSite')
    def test_available(self, IShoppingSite):
        instance = self.create_viewlet()
        self.assertEqual(instance.cart_total, IShoppingSite().locale_articles_total())
