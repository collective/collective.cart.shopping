# -*- coding: utf-8 -*-
from Testing import ZopeTestCase as ztc
from collective.cart.shopping.browser.template import OrderConfirmationView
from collective.cart.shopping.tests.base import IntegrationTestCase
from collective.cart.shopping.interfaces import IShoppingSite
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import directlyProvides
from zope.publisher.browser import TestRequest

import mock


class OrderConfirmationViewTestCase(IntegrationTestCase):
    """TestCase for OrderConfirmationView"""

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        ztc.utils.setupCoreSessions(self.layer['app'])

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseCheckOutView
        from collective.cart.shopping.browser.base import Message
        self.assertTrue(issubclass(OrderConfirmationView, (BaseCheckOutView, Message)))

    def test_name(self):
        self.assertEqual(getattr(OrderConfirmationView, 'grokcore.component.directive.name'), 'order-confirmation')

    def test_template(self):
        self.assertEqual(getattr(OrderConfirmationView, 'grokcore.view.directive.template'), 'order-confirmation')

    def create_view(self):
        request = TestRequest()
        request.set = mock.Mock()
        directlyProvides(request, IAttributeAnnotatable)
        return OrderConfirmationView(self.portal, request)

    @mock.patch('collective.cart.shopping.browser.template.IStatusMessage')
    def test_update(self, IStatusMessage):
        instance = self.create_view()
        self.portal.absolute_url = mock.Mock(return_value='portal_url')
        self.assertEqual(instance.update(), 'portal_url/@@billing-and-shipping')
        IStatusMessage().addStatusMessage.assert_called_with(u'info_missing_from_addresses', type='info')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 1)

        adapter = IShoppingSite(self.portal)
        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {})
        address = {
            'city': 'CITY',
            'email': 'fist.last@email.com',
            'first_name': 'FIRST',
            'last_name': 'LAST',
            'phone': 'PHONE',
            'street': 'STREET',
        }
        adapter.update_cart('billing', address)
        adapter.update_cart('shipping', address)

        self.assertIsNone(instance.update())
