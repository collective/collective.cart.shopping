# -*- coding: utf-8 -*-
from collective.cart.shopping.adapter.interface import CartArticleMultiAdapter
from collective.cart.shopping.interfaces import ICartArticleMultiAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.uuid.interfaces import IUUID

import mock


class CartArticleMultiAdapterTestCase(IntegrationTestCase):
    """TestCase for CartArticleMultiAdapter"""

    def test_subclass(self):
        self.assertTrue(issubclass(CartArticleMultiAdapter, object))
        from zope.interface import Interface
        self.assertTrue(issubclass(ICartArticleMultiAdapter, Interface))

    def test_instance(self):
        adapter = self.create_multiadapter(ICartArticleMultiAdapter)
        self.assertIsInstance(adapter, CartArticleMultiAdapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        adapter = self.create_multiadapter(ICartArticleMultiAdapter)
        self.assertTrue(verifyObject(ICartArticleMultiAdapter, adapter))

    def test_orig_article(self):
        article = {}
        adapter = self.create_multiadapter(ICartArticleMultiAdapter, obj=article)
        with self.assertRaises(KeyError):
            adapter.orig_article()

        orig_article = self.create_content('collective.cart.core.Article')
        uuid = IUUID(orig_article)
        article = {'id': uuid}
        adapter = self.create_multiadapter(ICartArticleMultiAdapter, obj=article)
        self.assertEqual(adapter.orig_article(), orig_article)

    @mock.patch('collective.cart.shopping.adapter.interface.IArticleAdapter')
    def test_image_url(self, IArticleAdapter):
        article = {}
        adapter = self.create_multiadapter(ICartArticleMultiAdapter, obj=article)
        adapter.orig_article = mock.Mock()
        self.assertEqual(adapter.image_url(), IArticleAdapter().image_url())

    def test_gross_subtotal(self):
        article = {'gross': self.money('12.40'), 'quantity': 2}
        adapter = self.create_multiadapter(ICartArticleMultiAdapter, obj=article)
        self.assertEqual(adapter.gross_subtotal(), self.money('24.80'))

    @mock.patch('collective.cart.shopping.adapter.interface.IStock')
    def test_quantity_max(self, IStock):
        article = {}
        adapter = self.create_multiadapter(ICartArticleMultiAdapter, obj=article)
        orig_article = mock.Mock()
        adapter.orig_article = mock.Mock(return_value=orig_article)
        adapter.quantity_max()
        IStock.assert_called_with(orig_article)
        self.assertEqual(adapter.quantity_max(), IStock().stock())

    def test_quantity_size(self):
        article = {}
        adapter = self.create_multiadapter(ICartArticleMultiAdapter, obj=article)
        adapter.quantity_max = mock.Mock(return_value=111)
        self.assertEqual(adapter.quantity_size(), 3)
