# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IAddSubtractStockViewlet
from collective.cart.shopping.browser.viewlet import AddSubtractStockViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class AddSubtractStockViewletTestCase(IntegrationTestCase):
    """TestCase for AddSubtractStockViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseArticleViewlet
        self.assertTrue(issubclass(AddSubtractStockViewlet, BaseArticleViewlet))
        from collective.cart.shopping.browser.interfaces import IBaseArticleViewlet
        self.assertTrue(issubclass(IAddSubtractStockViewlet, IBaseArticleViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(AddSubtractStockViewlet, context)
        self.assertTrue(verifyObject(IAddSubtractStockViewlet, instance))

    def test_stocks(self):
        context = self.create_content('collective.cart.core.Article')
        from collective.cart.shopping.browser.template import StockView
        view = self.create_view(StockView, context)
        instance = self.create_viewlet(AddSubtractStockViewlet, context, view)
        self.assertEqual(instance.stocks(), [])

        self.create_content('collective.cart.stock.Stock', context, title="Stock1",
            stock=1, money=self.money('1.00'), description="Description of Stock1")
        self.create_content('collective.cart.stock.Stock', context, title="Stock3",
            stock=3, money=self.money('3.00'), description="Description of Stock3")
        self.create_content('collective.cart.stock.Stock', context, title="Stock2",
            stock=2, money=self.money('2.00'), description="Description of Stock2")

        self.assertEqual(instance.stocks(), [{
            'oid': 'stock2',
            'current_stock': 2,
            'created': self.toLocalizedTime(),
            'url': 'http://nohost/plone/collective-cart-core-article/stock2',
            'money': self.money('2.00'),
            'title': 'Stock2',
            'initial_stock': 2,
            'description': 'Description of Stock2'
        }, {
            'oid': 'stock3',
            'current_stock': 3,
            'created': self.toLocalizedTime(),
            'url': 'http://nohost/plone/collective-cart-core-article/stock3',
            'money': self.money('3.00'),
            'title': 'Stock3',
            'initial_stock': 3,
            'description': 'Description of Stock3'
        }, {
            'oid': 'stock1',
            'current_stock': 1,
            'created': self.toLocalizedTime(),
            'url': 'http://nohost/plone/collective-cart-core-article/stock1',
            'money': self.money('1.00'),
            'title': 'Stock1', 'initial_stock': 1,
            'description': 'Description of Stock1'
        }])

    @mock.patch('collective.cart.shopping.browser.viewlet.IStatusMessage')
    def test_update(self, IStatusMessage):
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(AddSubtractStockViewlet, context)
        instance.context.restrictedTraverse = mock.Mock()
        instance.context.restrictedTraverse().current_base_url.return_value = 'CURRENT_BASE_URL'
        instance.request.form = {'form.buttons.QuickAdd': True, 'quick-add': 'AAA'}
        instance.add = mock.Mock(return_value={'max': 2})
        self.assertEqual(instance.update(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u'add_less_than_number', type='warn')

        instance.request.form = {'form.buttons.QuickSubtract': True, 'quick-subtract': 'AAA'}
        instance.subtract = mock.Mock(return_value={'max': 2})
        self.assertEqual(instance.update(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u'subtract_less_than_number', type='warn')
