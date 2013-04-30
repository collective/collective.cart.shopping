# -*- coding: utf-8 -*-
from collective.cart.core.interfaces import IOrderAdapter as IBaseOrderAdapter
from collective.cart.shopping.adapter.order import OrderAdapter
from collective.cart.shopping.interfaces import IOrderAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent import modified

import mock


class OrderAdapterTestCase(IntegrationTestCase):
    """TestCase for OrderAdapter"""

    def test_subclass(self):
        from collective.cart.core.adapter.order import OrderAdapter as BaseOrderAdapter
        self.assertTrue(issubclass(OrderAdapter, BaseOrderAdapter))
        self.assertTrue(issubclass(IOrderAdapter, IBaseOrderAdapter))

    def test_instance(self):
        context = self.create_content('collective.cart.core.Order')
        self.assertIsInstance(IOrderAdapter(context), OrderAdapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Order')
        self.assertTrue(verifyObject(IOrderAdapter, IOrderAdapter(context)))

    def test_articles(self):
        context = self.create_content('collective.cart.core.Order')
        adapter = IOrderAdapter(context)
        self.assertEqual(adapter.articles(), [])
        article1 = self.create_content('collective.cart.core.Article', id='articel1')
        uuid1 = IUUID(article1)
        order_article1 = self.create_content('collective.cart.core.OrderArticle', context, gross=self.money('10.00'),
            quantity=2, sku='111', vat_rate=24.0, title='Ärticle1', description='Description of Ärticle1', id=uuid1)
        order_article2 = self.create_content('collective.cart.core.OrderArticle', context, gross=self.money('5.00'),
            quantity=3, sku='222', vat_rate=24.0, title='Ärticle2', description='Description of Ärticle2')
        self.assertEqual(adapter.articles(), [
            {
                'description': u'Description of Ärticle1',
                'locale_gross_subtotal': u'20.00 €',
                'gross_subtotal': self.money('20.00'),
                'sku': '111',
                'gross': self.money('10.00'),
                'obj': order_article1,
                'title': u'Ärticle1',
                'url': 'http://nohost/plone/articel1',
                'image_url': 'http://nohost/plone/fallback.png',
                'vat_rate': u'24%',
                'quantity': 2,
                'id': uuid1,
            },
            {
                'description': u'Description of Ärticle2',
                'locale_gross_subtotal': u'15.00 €',
                'gross_subtotal': self.money('15.00'),
                'sku': '222',
                'gross': self.money('5.00'),
                'obj': order_article2,
                'title': u'Ärticle2',
                'url': None,
                'image_url': None,
                'vat_rate': u'24%',
                'quantity': 3,
                'id': 'collective-cart-core-orderarticle',
            }])

    def test_articles_total(self):
        context = self.create_content('collective.cart.core.Order')
        adapter = IOrderAdapter(context)
        adapter.articles = mock.Mock(return_value=[{'gross_subtotal': self.money('10.00')}, {'gross_subtotal': self.money('5.00')}])
        self.assertEqual(adapter.articles_total(), self.money('15.00'))

    def test_shipping_method(self):
        context = self.create_content('collective.cart.core.Order')
        adapter = IOrderAdapter(context)
        shipping_method = self.create_content('collective.cart.shipping.OrderShippingMethod', context)
        self.assertEqual(adapter.shipping_method().getObject(), shipping_method)

    def test_locale_shipping_method(self):
        context = self.create_content('collective.cart.core.Order')
        adapter = IOrderAdapter(context)
        self.assertIsNone(adapter.locale_shipping_method())
        shipping_method = self.create_content('collective.cart.shipping.OrderShippingMethod', context,
            gross=self.money('10.00'), title="Shipping Methöd", vat_rate=24.0)
        self.assertEqual(adapter.locale_shipping_method(), {
            'gross': u'10.00 €',
            'is_free': False,
            'title': 'Shipping Methöd',
            'vat_rate': 24.0
        })

        shipping_method.gross = self.money('0.00')
        modified(shipping_method)
        self.assertEqual(adapter.locale_shipping_method(), {
            'gross': u'0.00 €',
            'is_free': True,
            'title': 'Shipping Methöd',
            'vat_rate': 24.0
        })

    def test_total(self):
        context = self.create_content('collective.cart.core.Order')
        adapter = IOrderAdapter(context)
        adapter.articles_total = mock.Mock(return_value=self.money('10.00'))
        self.assertEqual(adapter.total(), self.money('10.00'))

        adapter.shipping_method = mock.Mock()
        adapter.shipping_method().gross = self.money('5.00')
        self.assertEqual(adapter.total(), self.money('15.00'))

    def test_get_address(self):
        context = self.create_content('collective.cart.core.Order')
        adapter = IOrderAdapter(context)
        billing = self.create_content('collective.cart.shopping.CustomerInfo', context, id='billing')
        shipping = self.create_content('collective.cart.shopping.CustomerInfo', context, id='shipping')
        self.assertEqual(adapter.get_address('billing').getObject(), billing)
        self.assertEqual(adapter.get_address('shipping').getObject(), billing)

        context.billing_same_as_shipping = False
        self.assertEqual(adapter.get_address('billing').getObject(), billing)
        self.assertEqual(adapter.get_address('shipping').getObject(), shipping)
