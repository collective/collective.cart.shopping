# -*- coding: utf-8 -*-
from Testing import ZopeTestCase as ztc
from collective.cart.shopping.browser.template import ShippingInfoView
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import directlyProvides
from zope.publisher.browser import TestRequest

import mock


class ShippingInfoViewTestCase(IntegrationTestCase):
    """TestCase for ShippingInfoView"""

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        ztc.utils.setupCoreSessions(self.layer['app'])

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseCheckOutView
        from collective.cart.shopping.browser.base import Message
        self.assertTrue(issubclass(ShippingInfoView, (BaseCheckOutView, Message)))

    def test_name(self):
        self.assertEqual(getattr(ShippingInfoView, 'grokcore.component.directive.name'), 'shipping-info')

    def test_template(self):
        self.assertEqual(getattr(ShippingInfoView, 'grokcore.view.directive.template'), 'shipping-info')

    def create_view(self):
        request = TestRequest()
        directlyProvides(request, IAttributeAnnotatable)
        return ShippingInfoView(self.portal, request)

    @mock.patch('collective.cart.shopping.browser.template.IShoppingSite')
    def test_shipping_info(self, IShoppingSite):
        instance = self.create_view()
        instance.shipping_info
        instance.shopping_site.get_info.assert_called_with('shipping')

    @mock.patch('collective.cart.shopping.browser.template.IStatusMessage')
    def test_update(self, IStatusMessage):
        instance = self.create_view()
        self.assertIsNone(instance.update())

        instance.request.form = {'form.buttons.back': True}
        self.portal.absolute_url = mock.Mock(return_value='portal_url')
        self.assertEqual(instance.update(), 'portal_url/@@billing-and-shipping')

        self.portal.restrictedTraverse = mock.Mock()
        self.portal.restrictedTraverse().current_base_url.return_value = 'current_base_url'

        instance.request.form = {'form.to.confirmation': True}
        self.assertEqual(instance.update(), 'current_base_url')
        IStatusMessage().addStatusMessage.assert_called_with(u'First name is missing.', type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 1)

        instance.request.form = {'form.to.confirmation': True, 'first_name': 'FIRST'}
        self.assertEqual(instance.update(), 'current_base_url')
        IStatusMessage().addStatusMessage.assert_called_with(u'Last name is missing.', type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 2)

        instance.request.form = {'form.to.confirmation': True, 'first_name': 'FIRST', 'last_name': 'LAST'}
        self.assertEqual(instance.update(), 'current_base_url')
        IStatusMessage().addStatusMessage.assert_called_with(u'Invalid e-mail address.', type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 3)

        instance.request.form = {'form.to.confirmation': True, 'first_name': 'FIRST', 'last_name': 'LAST',
            'email': 'fist.last@email.com'}
        self.assertEqual(instance.update(), 'current_base_url')
        IStatusMessage().addStatusMessage.assert_called_with(u'Street address is missing.', type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 4)

        instance.request.form = {'form.to.confirmation': True, 'first_name': 'FIRST', 'last_name': 'LAST',
            'email': 'fist.last@email.com',
            'street': 'STREET'}
        self.assertEqual(instance.update(), 'current_base_url')
        IStatusMessage().addStatusMessage.assert_called_with(u'City is missing.', type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 5)

        instance.request.form = {'form.to.confirmation': True, 'first_name': 'FIRST', 'last_name': 'LAST',
            'email': 'fist.last@email.com',
            'street': 'STREET',
            'city': 'CITY'}
        self.assertEqual(instance.update(), 'current_base_url')
        IStatusMessage().addStatusMessage.assert_called_with(u'Phone number is missing.', type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 6)

        instance.request.form = {'form.to.confirmation': True, 'first_name': 'FIRST', 'last_name': 'LAST',
            'email': 'fist.last@email.com',
            'street': 'STREET',
            'city': 'CITY',
            'phone': 'PHONE'}
        self.assertEqual(instance.update(), 'portal_url/@@order-confirmation')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 6)
        self.assertIsNone(instance.shopping_site.get_address('shipping'))

        session = instance.shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {})
        self.assertEqual(instance.update(), 'portal_url/@@order-confirmation')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 6)
        self.assertEqual(instance.shopping_site.get_address('shipping'), {
            'city': 'CITY',
            'email': 'fist.last@email.com',
            'first_name': 'FIRST',
            'last_name': 'LAST',
            'phone': 'PHONE',
            'street': 'STREET',
        })

        instance.request.form = {'form.to.confirmation': True, 'first_name': 'FIRST', 'last_name': 'LAST',
            'email': 'fist.last@email.com',
            'street': 'STREET',
            'city': 'CITY',
            'phone': 'PHONE',
            'organization': 'ORGANIZATION',
            'post': 'POST',
            'vat': 'VAT'}
        self.assertEqual(instance.update(), 'portal_url/@@order-confirmation')
        self.assertEqual(instance.shopping_site.get_address('shipping'), {
            'city': 'CITY',
            'email': 'fist.last@email.com',
            'first_name': 'FIRST',
            'last_name': 'LAST',
            'organization': 'ORGANIZATION',
            'phone': 'PHONE',
            'post': 'POST',
            'street': 'STREET',
            'vat': 'VAT',
        })
