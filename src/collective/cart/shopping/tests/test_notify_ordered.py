from collective.cart.shopping.subscriber import notify_ordered

import mock
import unittest


class TestCase(unittest.TestCase):
    """TestCase to test notify_ordered"""

    @mock.patch('collective.cart.shopping.subscriber.IStatusMessage')
    @mock.patch('collective.cart.shopping.subscriber.getToolByName')
    @mock.patch('collective.cart.shopping.subscriber.getUtility')
    @mock.patch('collective.cart.shopping.subscriber.ICartAdapter')
    @mock.patch('collective.cart.shopping.subscriber.IShoppingSite')
    def test_notify_ordered(self, IShoppingSite, ICartAdapter, getUtility, getToolByName, IStatusMessage):
        context = mock.Mock()
        event = mock.Mock()
        event.action = 'ordered'
        getToolByName().send = mock.Mock(side_effect=Exception)
        notify_ordered(context, event)
        IStatusMessage().addStatusMessage.assert_called_with(u'order-processed-but', type='warn')
