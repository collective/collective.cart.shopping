# -*- coding: utf-8 -*-
from collective.cart.core.browser.interfaces import ICartArticleListingViewlet
from collective.cart.shopping.browser.viewlet import CartArticleListingViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class CartArticleListingViewletTestCase(IntegrationTestCase):
    """TestCase for CartArticleListingViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCartArticleListingViewlet
        self.assertTrue(issubclass(CartArticleListingViewlet, BaseCartArticleListingViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(CartArticleListingViewlet)
        self.assertTrue(verifyObject(ICartArticleListingViewlet, instance))

    @mock.patch('collective.cart.shopping.browser.viewlet.IStock')
    @mock.patch('collective.cart.shopping.browser.viewlet.getMultiAdapter')
    def test_update(self, getMultiAdapter, IStock):
        from collective.cart.shopping.browser.template import CartView
        from zExceptions import Forbidden
        view = self.create_view(CartView)
        instance = self.create_viewlet(CartArticleListingViewlet, view=view)
        self.assertIsNone(instance.update())

        instance.context.restrictedTraverse = mock.Mock()
        instance.context.restrictedTraverse().verify.return_value = False
        instance.request.form = {'form.buttons.UpdateArticle': True}
        with self.assertRaises(Forbidden):
            instance.update()

        instance.context.restrictedTraverse().verify.return_value = True
        instance.view.shopping_site = mock.MagicMock()
        instance.request.form = {'form.buttons.UpdateArticle': 'UUID', 'UUID': '1'}
        article = self.create_content('collective.cart.core.Article', resucible_quantity=2)
        getMultiAdapter().orig_article.return_value = article
        instance.context.restrictedTraverse().current_base_url.return_value = 'CURRENT_BASE_URL'
        IStock().stock.return_value = 3
        IStock().reducible_quantity = 2
        self.assertEqual(instance.update(), 'CURRENT_BASE_URL')
