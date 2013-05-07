# -*- coding: utf-8 -*-
from collective.cart.shopping.adapter.interface import ShoppingSiteMultiAdapter
from collective.cart.shopping.interfaces import IShoppingSiteMultiAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase

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
    @mock.patch('collective.cart.shopping.adapter.interface.IArticleAdapter')
    @mock.patch('collective.cart.shopping.adapter.interface.IShoppingSite')
    @mock.patch('collective.cart.shopping.adapter.interface.IStatusMessage')
    def test_add_to_cart(self, IStatusMessage, IShoppingSite, IArticleAdapter, add_to_cart):
        adapter = self.create_multiadapter(IShoppingSiteMultiAdapter)
        self.assertIsNone(adapter.add_to_cart())

        adapter.context.restrictedTraverse = mock.Mock()
        adapter.request.form = {'form.buttons.AddToCart': 'UUID', 'quantity': '-1'}
        adapter.context.restrictedTraverse().current_base_url.return_value = 'CURRENT_BASE_URL'
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input positive integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 1)

        adapter.request.form = {'form.buttons.AddToCart': 'UUID'}
        IShoppingSite().get_object = mock.Mock(return_value=None)
        self.assertEqual(adapter.add_to_cart(), 'CURRENT_BASE_URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Not available to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 2)
