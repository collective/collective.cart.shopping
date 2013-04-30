# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.miscellaneous import Miscellaneous
from collective.cart.shopping.tests.base import IntegrationTestCase


class MiscellaneousTestCase(IntegrationTestCase):
    """TestCase for Miscellaneous"""

    def test_subclass(self):
        from Products.Five.browser import BrowserView
        self.assertTrue(issubclass(Miscellaneous, BrowserView))

    def test_is_article(self):
        instance = self.create_view(Miscellaneous)
        self.assertFalse(instance.is_article())

        article = self.create_content('collective.cart.core.Article', money=self.money('12.40'), vat_rate=24.0)
        instance = self.create_view(Miscellaneous, article)
        self.assertTrue(instance.is_article())
