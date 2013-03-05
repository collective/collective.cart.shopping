from collective.cart.shopping.browser.viewlet import CartContentViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class CartContentViewletTestCase(IntegrationTestCase):
    """TestCase for CartContentViewlet"""

    def test_subclass(self):
        from collective.cart.core.browser.viewlet import CartContentViewlet as BaseCartContentViewlet
        self.assertTrue(issubclass(CartContentViewlet, BaseCartContentViewlet))

    def test_layer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        self.assertEqual(getattr(CartContentViewlet, 'grokcore.view.directive.layer'),
            ICollectiveCartShoppingLayer)

    def test_order(self):
        cart = self.create_content('collective.cart.core.Cart')
        instance = self.create_viewlet(CartContentViewlet, cart)
        self.assertEqual(instance.order, {
            'articles': [],
            'billing_info': None,
            'id': 'collective-cart-core.cart',
            'modified': self.ulocalized_time(self.portal.modified()),
            'shipping_info': None,
            'shipping_method': None,
            'state_title': 'Created',
            'title': '',
            'total': self.money('0.00'),
            'url': 'http://nohost/plone/collective-cart-core.cart'
        })
