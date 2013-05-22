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

    # @mock.patch('plone.app.layout.globals.context.ContextState.current_base_url', mock.Mock(return_value='http://nohost/plone/portal_registration/passwordreset/51cac7879c3b6c1de9a7d9747177476e'))
    # def test_is_check_out_view(self):
    #     instance = self.create_view(Miscellaneous)
    #     self.assertFalse(instance.is_check_out_view())
