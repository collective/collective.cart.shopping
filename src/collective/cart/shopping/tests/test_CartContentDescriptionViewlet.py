from collective.cart.shopping.browser.viewlet import CartContentDescriptionViewlet

import unittest


class CartContentDescriptionViewletTestCase(unittest.TestCase):
    """TestCase for CartContentDescriptionViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCartContentViewlet
        self.assertTrue(issubclass(CartContentDescriptionViewlet, BaseCartContentViewlet))

    def test_name(self):
        self.assertEqual(getattr(CartContentDescriptionViewlet, 'grokcore.component.directive.name'),
            'collective.cart.shopping.order.description')

    def test_template(self):
        self.assertTrue(getattr(CartContentDescriptionViewlet, 'grokcore.view.directive.template'), 'cart-content-description')
