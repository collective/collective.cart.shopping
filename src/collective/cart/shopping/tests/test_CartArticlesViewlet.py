from collective.cart.shopping.browser.viewlet import CartArticlesViewlet

import unittest


class CartArticlesViewletTestCase(unittest.TestCase):
    """TestCase for CartArticlesViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCartArticlesViewlet
        self.assertTrue(issubclass(CartArticlesViewlet, BaseCartArticlesViewlet))
