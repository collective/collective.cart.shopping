from collective.cart.shopping.browser.viewlet import BaseAddToCartViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest

import mock


class BaseAddToCartViewletTestCase(IntegrationTestCase):
    """TestCase for BaseAddToCartViewlet"""

    def test_subclass(self):
        from collective.cart.core.browser.viewlet import AddToCartViewlet
        self.assertTrue(issubclass(BaseAddToCartViewlet, AddToCartViewlet))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseAddToCartViewlet, 'martian.martiandirective.baseclass'))

    def test_layer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        self.assertEqual(getattr(BaseAddToCartViewlet, 'grokcore.view.directive.layer'), ICollectiveCartShoppingLayer)

    def test_viewletmanager(self):
        from collective.cart.shopping.browser.viewlet import AddToCartViewletManager
        self.assertEqual(getattr(BaseAddToCartViewlet, 'grokcore.viewlet.directive.viewletmanager'), AddToCartViewletManager)

    def create_viewlet(self):
        context = mock.Mock()
        request = TestRequest()
        return BaseAddToCartViewlet(context, request, None, None)

    def test_quantity_size(self):
        instance = self.create_viewlet()
        self.assertIsNone(instance.quantity_size)

        setattr(instance, 'quantity_max', 0)
        self.assertEqual(instance.quantity_size, 1)

        setattr(instance, 'quantity_max', 10)
        self.assertEqual(instance.quantity_size, 2)
