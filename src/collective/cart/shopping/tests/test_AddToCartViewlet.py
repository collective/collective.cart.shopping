# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IAddToCartViewlet
from collective.cart.shopping.browser.viewlet import AddToCartViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest
from collective.cart.shopping.browser.template import ArticleView

import mock


class AddToCartViewletTestCase(IntegrationTestCase):
    """TestCase for AddToCartViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseAddToCartViewlet
        self.assertTrue(issubclass(AddToCartViewlet, BaseAddToCartViewlet))
        from collective.cart.shopping.browser.interfaces import IBaseAddToCartViewlet
        self.assertTrue(issubclass(IAddToCartViewlet, IBaseAddToCartViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(AddToCartViewlet, context)
        self.assertTrue(verifyObject(IAddToCartViewlet, instance))

    # @mock.patch('collective.cart.shopping.browser.viewlet.getMultiAdapter')
    # def test_update(self, getMultiAdapter):
    #     context = self.create_content('collective.cart.core.Article')
    #     instance = self.create_viewlet(AddToCartViewlet, context)
    #     instance.update()
    #     self.assertTrue(getMultiAdapter().add_to_cart.called)

    # @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    # def test_quantity_max(self, IArticleAdapter):
    #     context = self.create_content('collective.cart.core.Article')
    #     instance = self.create_viewlet(AddToCartViewlet, context)
    #     IArticleAdapter().quantity_max.return_value = 10
    #     self.assertEqual(instance.quantity_max(), 10)

    # def test_soldout(self):
    #     context = self.create_content('collective.cart.core.Article')
    #     view = self.create_view(ArticleView, context)
    #     instance = self.create_viewlet(AddToCartViewlet, context, view=view)
    #     instance.adapter = mock.Mock()
    #     instance.adapter().soldout.return_value = True
    #     self.assertTrue(instance.soldout())

    #     instance.adapter().soldout.return_value = False
    #     self.assertFalse(instance.soldout())

    # @mock.patch('collective.cart.shopping.browser.viewlet.IUUID', mock.Mock(return_value='UUID'))
    # def test_uuid(self):
    #     context = self.create_content('collective.cart.core.Article')
    #     instance = self.create_viewlet(AddToCartViewlet, context)
    #     self.assertEqual(instance.uuid(), 'UUID')
