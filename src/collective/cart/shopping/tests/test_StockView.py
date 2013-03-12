# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.template import StockView
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class StockViewTestCase(IntegrationTestCase):
    """TestCase for StockView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseArticleView
        self.assertTrue(issubclass(StockView, BaseArticleView))

    def test_name(self):
        self.assertEqual(getattr(StockView, 'grokcore.component.directive.name'), 'stock')

    def test_require(self):
        self.assertEqual(getattr(StockView, 'grokcore.security.directive.require'), ['cmf.ModifyPortalContent'])

    def test_template(self):
        self.assertEqual(getattr(StockView, 'grokcore.view.directive.template'), 'stock')

    @mock.patch('collective.cart.shopping.browser.template.IStockBehavior')
    def test_stock(self, IStockBehavior):
        IStockBehavior().stock = 100
        context = mock.Mock()
        instance = self.create_view(StockView, context)
        self.assertEqual(instance.stock, 100)

    def test_stocks(self):
        article = self.create_content('collective.cart.core.Article', id='article',
            money=self.money('12.40'), vat=self.decimal('24.00'))
        instance = self.create_view(StockView, article)
        self.assertEqual(len(instance.stocks), 0)

        stock1 = self.create_content('collective.cart.stock.Stock', article, id='stock1', title='Stöck1', stock=10,
            description="Description of Stöck1", money=self.money('1.00'))
        self.assertEqual(instance.stocks, [{
            'created': self.ulocalized_time(stock1.created()),
            'current_stock': 10,
            'description': 'Description of Stöck1',
            'initial_stock': 10,
            'money': self.money('1.00'),
            'oid': 'stock1',
            'title': 'Stöck1',
            'url': 'http://nohost/plone/article/stock1'
        }])

        self.create_content('collective.cart.stock.Stock', article, id="stock3", stock=20, description="Description of Stöck3",
            money=self.money('3.00'), title="Stöck3")
        self.create_content('collective.cart.stock.Stock', article, id="stock2", stock=20, description="Description of Stöck2",
            money=self.money('2.00'), title="Stöck2")

        self.assertEqual(len(instance.stocks), 3)
        # self.assertEqual([stock['title'] for stock in instance.stocks], ['Stöck2', 'Stöck3', 'Stöck1'])

    @mock.patch('collective.cart.shopping.browser.template.IStockBehavior')
    def test_add(self, IStockBehavior):
        context = mock.Mock()
        instance = self.create_view(StockView, context)
        IStockBehavior().initial_stock = 100
        IStockBehavior().stock = 100
        self.assertIsNone(instance.add)

        IStockBehavior().stock = 40
        self.assertEqual(instance.add, {'max': 60, 'size': 2})

    @mock.patch('collective.cart.shopping.browser.template.IStockBehavior')
    def test_subtract(self, IStockBehavior):
        context = mock.Mock()
        instance = self.create_view(StockView, context)
        IStockBehavior().stock = 0
        self.assertIsNone(instance.subtract)

        IStockBehavior().stock = 40
        self.assertEqual(instance.subtract, {'max': 40, 'size': 2})

    @mock.patch('collective.cart.shopping.browser.template.IStatusMessage')
    @mock.patch('collective.cart.shopping.browser.template.IStockBehavior')
    @mock.patch('collective.cart.shopping.browser.template.getMultiAdapter')
    def test_update(self, getMultiAdapter, IStockBehavior, IStatusMessage):
        article = self.create_content('collective.cart.core.Article', id='article',
            money=self.money('12.40'), vat=self.decimal('24.00'))
        instance = self.create_view(StockView, article)
        getMultiAdapter().current_base_url.return_value = 'URL'
        self.assertIsNone(instance.update())

        IStockBehavior().initial_stock = 100
        IStockBehavior().stock = 40
        instance.request.form = {'form.buttons.QuickAdd': True}
        self.assertEqual(instance.update(), 'URL')
        IStatusMessage().addStatusMessage.assert_called_with(u'add_less_than_number', type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 1)

        instance.request.form = {'form.buttons.QuickAdd': True, 'quick-add': '10'}
        self.assertEqual(instance.update(), 'URL')
        IStockBehavior().add_stock.assert_called_with(10)
        IStatusMessage().addStatusMessage.assert_called_with(u'successfully_added_number', type='info')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 2)

        instance.request.form = {'form.buttons.QuickSubtract': True}
        self.assertEqual(instance.update(), 'URL')
        IStatusMessage().addStatusMessage.assert_called_with(u'subtract_less_than_number', type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 3)

        instance.request.form = {'form.buttons.QuickSubtract': True, 'quick-subtract': '10'}
        self.assertEqual(instance.update(), 'URL')
        IStockBehavior().sub_stock.assert_called_with(10)
        IStatusMessage().addStatusMessage.assert_called_with(u'successfully_subtracted_number', type='info')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 4)

        instance.request.form = {'form.buttons.AddNewStock': True}
        instance.context.absolute_url = mock.Mock(return_value='context_url')
        self.assertEqual(instance.update(), 'context_url/++add++collective.cart.stock.Stock')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 4)

        self.create_content('collective.cart.stock.Stock', article, id='stock1', title='Stöck1', stock=10,
            description="Description of Stöck1", money=self.money('1.00'))
        self.assertIsNotNone(article['stock1'])
        instance.request.form = {'form.buttons.Remove': 'stock2'}
        with self.assertRaises(AttributeError):
            instance.update()
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 4)

        instance.request.form = {'form.buttons.Remove': 'stock1'}
        self.assertEqual(instance.update(), 'URL')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 4)
