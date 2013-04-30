# -*- coding: utf-8 -*-
# from collective.cart.shopping.browser.viewlet import OrderContentViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class OrderContentViewletTestCase(IntegrationTestCase):
    """TestCase for OrderContentViewlet"""

    def test(self):
        pass

    # def test_subclass(self):
    #     from collective.cart.core.browser.viewlet import OrderContentViewlet as BaseOrderContentViewlet
    #     self.assertTrue(issubclass(OrderContentViewlet, BaseOrderContentViewlet))

    # def test_order(self):
    #     cart = self.create_content('collective.cart.core.Cart')
    #     instance = self.create_viewlet(OrderContentViewlet, cart)
    #     self.assertEqual(instance.order, {
    #         'articles': [],
    #         'billing_info': None,
    #         'id': 'collective-cart-core.cart',
    #         'modified': self.ulocalized_time(self.portal.modified()),
    #         'registration_number': None,
    #         'shipping_info': None,
    #         'shipping_method': None,
    #         'state_title': 'Created',
    #         'title': '',
    #         'total': u'0.00 €',
    #         'url': 'http://nohost/plone/collective-cart-core.cart'
    #     })
