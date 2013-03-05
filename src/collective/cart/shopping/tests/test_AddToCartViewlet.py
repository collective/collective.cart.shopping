from collective.cart.shopping.browser.viewlet import AddToCartViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest

import mock


class AddToCartViewletTestCase(IntegrationTestCase):
    """TestCase for AddToCartViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseAddToCartViewlet
        self.assertTrue(issubclass(AddToCartViewlet, BaseAddToCartViewlet))

    def create_viewlet(self):
        context = mock.Mock()
        request = TestRequest()
        return AddToCartViewlet(context, request, None, None)

    @mock.patch('collective.cart.shopping.browser.viewlet.getMultiAdapter')
    def test_update(self, getMultiAdapter):
        instance = self.create_viewlet()
        instance.update()
        self.assertTrue(getMultiAdapter().add_to_cart.called)

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_quantity_max(self, IArticleAdapter):
        instance = self.create_viewlet()
        IArticleAdapter().quantity_max = 10
        self.assertEqual(instance.quantity_max, 10)

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_soldout(self, IArticleAdapter):
        instance = self.create_viewlet()
        IArticleAdapter().soldout = True
        self.assertTrue(instance.soldout)

        IArticleAdapter().soldout = False
        self.assertFalse(instance.soldout)

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_available(self, IArticleAdapter):
        instance = self.create_viewlet()
        IArticleAdapter().addable_to_cart = True
        self.assertTrue(instance.available)

        IArticleAdapter().addable_to_cart = False
        self.assertFalse(instance.available)

    @mock.patch('collective.cart.shopping.browser.viewlet.IUUID', mock.Mock(return_value='UUID'))
    def test_uuid(self):
        instance = self.create_viewlet()
        self.assertEqual(instance.uuid, 'UUID')
