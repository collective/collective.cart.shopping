# -*- coding: utf-8 -*-
from collective.cart.shopping.adapter.order_article import OrderArticleAdapter
from collective.cart.shopping.interfaces import IOrderArticleAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase


class OrderArticleAdapterTestCase(IntegrationTestCase):
    """TestCase for OrderArticleAdapter"""

    def test_subclass(self):
        from collective.base.adapter import Adapter
        self.assertTrue(issubclass(OrderArticleAdapter, Adapter))
        from collective.base.interfaces import IAdapter
        self.assertTrue(issubclass(IOrderArticleAdapter, IAdapter))

    def test_instance(self):
        context = self.create_content('collective.cart.core.OrderArticle')
        self.assertIsInstance(IOrderArticleAdapter(context), OrderArticleAdapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.OrderArticle')
        self.assertTrue(verifyObject(IOrderArticleAdapter, IOrderArticleAdapter(context)))

    def test_gross_subtotal(self):
        context = self.create_content('collective.cart.core.OrderArticle')
        context.gross = self.money('20.00')
        context.quantity = 2
        adapter = IOrderArticleAdapter(context)
        self.assertEqual(adapter.gross_subtotal(), self.money('40.00'))
