from collective.cart.shopping.browser.interfaces import IOrderListingViewletManager
from collective.cart.shopping.browser.viewletmanager import OrderListingViewletManager
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class OrderListingViewletManagerTestCase(IntegrationTestCase):
    """TestCase for OrderListingViewletManager"""

    def test_subclass(self):
        from collective.base.viewletmanager import RepeatedViewletManager as Base
        self.assertTrue(issubclass(OrderListingViewletManager, Base))
        from collective.base.interfaces import IRepeatedViewletManager as Base
        self.assertTrue(issubclass(IOrderListingViewletManager, Base))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = mock.Mock()
        instance = OrderListingViewletManager(context, None, None)
        self.assertTrue(verifyObject(IOrderListingViewletManager, instance))

    def test_items(self):
        context = mock.Mock()
        instance = OrderListingViewletManager(context, None, None)
        instance.items = mock.Mock(return_value=[mock.Mock(), mock.Mock()])
        self.assertEqual(instance.class_collapsible(), 'collapsible collapsedOnLoad')
