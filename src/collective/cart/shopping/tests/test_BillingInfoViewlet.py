# -*- coding: utf-8 -*-
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.browser.viewlet import BillingInfoViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.interface import alsoProvides
from zope.publisher.browser import TestRequest

import mock


class BillingInfoViewletTestCase(IntegrationTestCase):
    """TestCase for BillingInfoViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseShoppingSiteRootViewlet
        self.assertTrue(issubclass(BillingInfoViewlet, BaseShoppingSiteRootViewlet))

    def test_name(self):
        self.assertTrue(getattr(BillingInfoViewlet, 'grokcore.component.directive.name'), 'collective.cart.shopping.billing.info')

    def test_template(self):
        self.assertTrue(getattr(BillingInfoViewlet, 'grokcore.view.directive.template'), 'billing-info')

    def test_viewletmanager(self):
        from collective.cart.shopping.browser.viewlet import BillingAndShippingViewletManager
        self.assertTrue(getattr(BillingInfoViewlet, 'grokcore.viewlet.directive.viewletmanager'), BillingAndShippingViewletManager)

    def create_viewlet(self):
        request = TestRequest()
        return BillingInfoViewlet(self.portal, request, None, None)

    @mock.patch('collective.cart.shopping.browser.viewlet.IShoppingSite')
    def test_billing_info(self, IShoppingSite):
        instance = self.create_viewlet()
        self.assertEqual(instance.billing_info, IShoppingSite().get_info())

    def test_shipping_methods(self):
        instance = self.create_viewlet()
        with self.assertRaises(TypeError):
            instance.shipping_methods

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertEqual(len(instance.shipping_methods), 0)

        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id="shipping-method-container")
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1', title='ShippingMethöd1',
            description="Description of Shippingmethöd1")
        uuid1 = IUUID(shippingmethod1)
        shippingmethod2 = self.create_atcontent('ShippingMethod', container, id='shippingmethod2', title='ShippingMethöd2',
            description="Description of Shippingmethöd2")
        uuid2 = IUUID(shippingmethod2)

        with self.assertRaises(TypeError):
            instance.shipping_methods

        session = IShoppingSite(self.portal).getSessionData(create=True)
        session.set('collective.cart.core', {'shipping_method': {'uuid': 'UUID'}})
        self.assertEqual(instance.shipping_methods, [{
            'checked': False,
            'description': 'Description of Shippingmethöd1',
            'title': 'ShippingMethöd1  0.00 EUR',
            'uuid': uuid1,
        }, {
            'checked': False,
            'description': 'Description of Shippingmethöd2',
            'title': 'ShippingMethöd2  0.00 EUR',
            'uuid': uuid2,
        }])

        session.set('collective.cart.core', {'shipping_method': {'uuid': uuid1}})
        self.assertEqual(instance.shipping_methods, [{
            'checked': True,
            'description': 'Description of Shippingmethöd1',
            'title': 'ShippingMethöd1  0.00 EUR',
            'uuid': uuid1,
        }, {
            'checked': False,
            'description': 'Description of Shippingmethöd2',
            'title': 'ShippingMethöd2  0.00 EUR',
            'uuid': uuid2,
        }])

    def test_single_shipping_method(self):
        instance = self.create_viewlet()
        with self.assertRaises(TypeError):
            instance.single_shipping_method

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertFalse(instance.single_shipping_method)

        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id="shipping-method-container")
        self.create_atcontent('ShippingMethod', container, id='shippingmethod1', title='ShippingMethöd1',
            description="Description of Shippingmethöd1")

        with self.assertRaises(TypeError):
            instance.single_shipping_method

        session = IShoppingSite(self.portal).getSessionData(create=True)
        session.set('collective.cart.core', {'shipping_method': {'uuid': 'UUID'}})
        self.assertTrue(instance.single_shipping_method)

        self.create_atcontent('ShippingMethod', container, id='shippingmethod2', title='ShippingMethöd2',
            description="Description of Shippingmethöd2")

        self.assertFalse(instance.single_shipping_method)

    def test_billing_same_as_shipping(self):
        instance = self.create_viewlet()
        with self.assertRaises(AttributeError):
            instance.billing_same_as_shipping

        session = IShoppingSite(self.portal).getSessionData(create=True)
        session.set('collective.cart.core', {})
        self.assertTrue(instance.billing_same_as_shipping)

        session.set('collective.cart.core', {'billing_same_as_shipping': False})
        self.assertFalse(instance.billing_same_as_shipping)

        session.set('collective.cart.core', {'billing_same_as_shipping': True})
        self.assertTrue(instance.billing_same_as_shipping)
