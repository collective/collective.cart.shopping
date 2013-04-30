from collective.cart.core.browser.viewlet import CartArticleListingViewlet

import unittest


class BaseCartArticleListingViewletTestCase(unittest.TestCase):
    """TestCase for BaseCartArticleListingViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCartArticleListingViewlet
        self.assertTrue(issubclass(BaseCartArticleListingViewlet, CartArticleListingViewlet))
