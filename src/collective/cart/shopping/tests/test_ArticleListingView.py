# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IArticleListingView
from collective.cart.shopping.browser.template import ArticleListingView
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class ArticleListingViewTestCase(IntegrationTestCase):
    """TestCase for ArticleListingView"""

    def test_subclass(self):
        from Products.Five.browser import BrowserView
        self.assertTrue(issubclass(ArticleListingView, BrowserView))
        from collective.cart.core.browser.interfaces import IBaseFormView
        self.assertTrue(issubclass(IArticleListingView, IBaseFormView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(ArticleListingView)
        self.assertTrue(verifyObject(IArticleListingView, instance))

    def test_table_headers(self):
        instance = self.create_view(ArticleListingView)
        self.assertEqual(instance.table_headers(), (u'SKU', u'Name', u'Price', u'Stock', u'Subtotal'))

    @mock.patch('collective.cart.shopping.browser.template.IStockBehavior')
    def test_articles(self, IStockBehavior):
        instance = self.create_view(ArticleListingView)
        self.assertEqual(len(instance.articles()), 0)

        IStockBehavior().stocks.return_value = None
        IStockBehavior().stock.return_value = 0
        self.create_content('collective.cart.core.Article', id='article1', title='Ärticle1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'), sku='1')
        self.assertEqual(instance.articles(), [
            {'sku': '1', 'title': 'Ärticle1', 'url': 'http://nohost/plone/article1', 'price': 'N/A', 'subtotal': 'N/A', 'stock': 0}])

        IStockBehavior().stock.return_value = 10
        stock = mock.Mock()
        stock.price = 5.0
        IStockBehavior().stocks.return_value = [stock]
        self.assertEqual(instance.articles(), [
            {'sku': '1', 'title': 'Ärticle1', 'url': 'http://nohost/plone/article1', 'price': '5.00', 'subtotal': '50.00', 'stock': 10}])

    def test___call__(self):
        instance = self.create_view(ArticleListingView)
        with self.assertRaises(AttributeError):
            instance()
        instance.request.form = {'form.buttons.Export': True}
        self.assertEqual(instance(), 'SKU|Name|Price|Stock|Subtotal\r\n')
        self.assertEqual(instance.request.response.getHeader('Content-Type'), 'text/csv')
        self.assertTrue(instance.request.response.getHeader("Content-Disposition").startswith('attachment; filename="stock-'))
        self.assertTrue(instance.request.response.getHeader("Content-Disposition").endswith('.csv"'))

        self.create_content('collective.cart.core.Article', id='article1', sku=u'SKÖ1',
            money=self.money('12.40'), vat_rate=24.0)
        self.assertEqual(instance(), 'SKU|Name|Price|Stock|Subtotal\r\nSKÖ1||N/A|0|N/A\r\n')
