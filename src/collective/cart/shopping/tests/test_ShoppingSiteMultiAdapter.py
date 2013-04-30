# -*- coding: utf-8 -*-
from collective.cart.shopping.adapter.interface import ShoppingSiteMultiAdapter
from collective.cart.shopping.interfaces import IShoppingSiteMultiAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money

import mock


class ShoppingSiteMultiAdapterTestCase(IntegrationTestCase):
    """TestCase for ShoppingSiteMultiAdapter"""

    def test_subclass(self):
        self.assertTrue(issubclass(ShoppingSiteMultiAdapter, object))
        from zope.interface import Interface
        self.assertTrue(issubclass(IShoppingSiteMultiAdapter, Interface))

    def test_instance(self):
        adapter = self.create_multiadapter(IShoppingSiteMultiAdapter)
        self.assertIsInstance(adapter, ShoppingSiteMultiAdapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        adapter = self.create_multiadapter(IShoppingSiteMultiAdapter)
        self.assertTrue(verifyObject(IShoppingSiteMultiAdapter, adapter))

    @mock.patch('collective.cart.core.adapter.article.ArticleAdapter.add_to_cart')
    @mock.patch('collective.cart.shopping.adapter.interface.IShoppingSite')
    @mock.patch('collective.cart.shopping.adapter.interface.IStatusMessage')
    def test_add_to_cart(self, IStatusMessage, IShoppingSite, add_to_cart):
        adapter = self.create_multiadapter(IShoppingSiteMultiAdapter)
        self.assertIsNone(adapter.add_to_cart())

        adapter.context.restrictedTraverse = mock.Mock()
        adapter.context.restrictedTraverse().verify.return_value = False
        adapter.request.form = {'subarticle': 'UUID'}
        from zExceptions import Forbidden
        with self.assertRaises(Forbidden):
            adapter.add_to_cart()

        adapter.request.form = {'subarticle': 'UUID'}
        adapter.context.restrictedTraverse().verify.return_value = True
        adapter.context.restrictedTraverse().current_base_url.return_value = 'CURRENT_BASE_URL'
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 1)

        adapter.request.form = {'form.buttons.AddToCart': 'UUID'}
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 2)

        adapter.request.form = {'subarticle': 'UUID', 'quantity': 'QUANTITY'}
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 3)

        adapter.request.form = {'subarticle': 'UUID', 'quantity': '-2'}
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input positive integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 4)

        IShoppingSite().get_object.return_value = None
        adapter.request.form = {'subarticle': 'UUID', 'quantity': '2'}
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Not available to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 5)

        article1 = self.create_content('collective.cart.core.Article', id='article1',
            money=Money(Decimal('12.40'), 'EUR'), vat_rate=24.0, sku="SKÖ1", reducible_quantity=100)

        IShoppingSite().get_object.return_value = article1

        adapter.request.form = {'subarticle': 'UUID', 'quantity': '2'}
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Not available to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 6)

        self.create_content('collective.cart.stock.Stock', article1, id='stock1', stock=100, reducible_quantity=100)

        adapter.request.form = {'subarticle': 'UUID', 'quantity': '2'}
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 6)
        add_to_cart.assert_called_with(sku='SKÖ1', gross=self.money('12.40'), weight=0.0, title='', height=0.0, width=0.0, depth=0.0, vat_rate=24.0, net=self.money('10.00'), vat=self.money('2.40'), quantity=2)
