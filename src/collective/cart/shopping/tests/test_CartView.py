from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.browser.template import CartView
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.interface import alsoProvides

import mock


class CartViewTestCase(IntegrationTestCase):
    """TestCase for CartView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseCheckOutView
        from collective.cart.core.browser.template import CartView as BaseCartView
        from collective.cart.shopping.browser.base import Message
        self.assertTrue(issubclass(CartView, (BaseCheckOutView, BaseCartView, Message)))

    def test_update(self):
        instance = self.create_view(CartView)
        instance.request = mock.Mock()
        instance.update()
        instance.request.response.redirect.assert_called_with('http://nohost/plone/@@cart')
        self.assertEqual(instance.request.response.redirect.call_count, 1)

        shopping_site = IShoppingSite(self.portal)
        alsoProvides(self.portal, IShoppingSiteRoot)
        instance.update()
        instance.request.response.redirect.assert_called_with('http://nohost/plone/@@cart')
        self.assertEqual(instance.request.response.redirect.call_count, 2)
        self.assertIsNone(shopping_site.shipping_method)

        article = self.create_content('collective.cart.core.Article', id='article',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        self.create_content('collective.cart.stock.Stock', article, stock=10)
        IArticleAdapter(article).add_to_cart()
        instance.update()
        instance.request.response.redirect.assert_called_with('http://nohost/plone/@@cart')
        self.assertEqual(instance.request.response.redirect.call_count, 2)
        self.assertIsNone(shopping_site.shipping_method)

        container = self.create_content('collective.cart.shipping.ShippingMethodContainer')
        self.create_atcontent('ShippingMethod', container, id='shipping_method')
        instance.update()
        instance.request.response.redirect.assert_called_with('http://nohost/plone/@@cart')
        self.assertEqual(instance.request.response.redirect.call_count, 2)
        self.assertIsNotNone(shopping_site.shipping_method)
