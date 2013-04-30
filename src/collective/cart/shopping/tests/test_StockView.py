# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IStockView
from collective.cart.shopping.browser.template import StockView
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class StockViewTestCase(IntegrationTestCase):
    """TestCase for StockView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseArticleView
        self.assertTrue(issubclass(StockView, BaseArticleView))
        from collective.cart.shopping.browser.interfaces import IBaseArticleView
        self.assertTrue(issubclass(IStockView, IBaseArticleView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article', title="Ärticle")
        instance = self.create_view(StockView, context)
        self.assertTrue(verifyObject(IStockView, instance))

    @mock.patch('collective.cart.shopping.browser.template.IStockBehavior')
    def test_stock(self, IStockBehavior):
        IStockBehavior().stock.return_value = 100
        context = mock.Mock()
        instance = self.create_view(StockView, context)
        self.assertEqual(instance.stock(), 100)
