# -*- coding: utf-8 -*-
from Testing import ZopeTestCase as ztc
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.core.session import SessionArticles
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IShoppingSiteMultiAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.uuid.interfaces import IUUID
from zope.interface import alsoProvides

import mock


class ShoppingSiteMultiAdapterTestCase(IntegrationTestCase):
    """TestCase for ShoppingSiteMultiAdapter"""

    def setUp(self):
        from plone.app.testing import TEST_USER_ID
        from plone.app.testing import setRoles
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        ztc.utils.setupCoreSessions(self.layer['app'])

    def test_subclass(self):
        from five.grok import MultiAdapter
        from collective.cart.shopping.adapter.interface import ShoppingSiteMultiAdapter
        self.assertTrue(issubclass(ShoppingSiteMultiAdapter, MultiAdapter))
        from zope.interface import Interface
        self.assertTrue(issubclass(IShoppingSiteMultiAdapter, Interface))

    def test_adapts(self):
        from collective.cart.shopping.adapter.interface import ShoppingSiteMultiAdapter
        from zope.interface import Interface
        from zope.publisher.interfaces.browser import IBrowserRequest
        self.assertEqual(ShoppingSiteMultiAdapter.__component_adapts__, (Interface, IBrowserRequest))

    def test_provides(self):
        from collective.cart.shopping.adapter.interface import ShoppingSiteMultiAdapter
        self.assertEqual(getattr(ShoppingSiteMultiAdapter, 'grokcore.component.directive.provides'), IShoppingSiteMultiAdapter)

    @mock.patch('collective.cart.shopping.adapter.interface.IStatusMessage')
    @mock.patch('collective.cart.shopping.adapter.interface.getMultiAdapter')
    def test_add_to_cart(self, getMultiAdapter, IStatusMessage):
        adapter = self.create_multiadapter(IShoppingSiteMultiAdapter)
        self.assertIsNone(adapter.add_to_cart())

        getMultiAdapter().current_base_url.return_value = 'URL'

        adapter.request.form = {'subarticle': 'UUID'}
        self.assertEqual(adapter.add_to_cart(), 'URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 1)

        adapter.request.form = {'form.buttons.AddToCart': 'UUID'}
        self.assertEqual(adapter.add_to_cart(), 'URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 2)

        adapter.request.form = {'subarticle': 'UUID', 'quantity': 'QUANTITY'}
        self.assertEqual(adapter.add_to_cart(), 'URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 3)

        adapter.request.form = {'subarticle': 'UUID', 'quantity': '-2'}
        self.assertEqual(adapter.add_to_cart(), 'URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Input positive integer value to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 4)

        adapter.request.form = {'subarticle': 'UUID', 'quantity': '2'}
        self.assertEqual(adapter.add_to_cart(), 'URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Not available to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 5)

        article1 = self.create_content('collective.cart.core.Article', id='article1',
            money=Money(Decimal('12.40'), 'EUR'), vat_rate=Decimal('24.00'), sku="SKÖ1", reducible_quantity=100)
        uuid1 = IUUID(article1)

        adapter.request.form = {'subarticle': uuid1, 'quantity': '2'}
        self.assertEqual(adapter.add_to_cart(), 'URL')
        IStatusMessage().addStatusMessage.assert_called_with(u"Not available to add to cart.", type='warn')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 6)

        alsoProvides(self.portal, IShoppingSiteRoot)
        article1.salable = True
        self.create_content('collective.cart.stock.Stock', article1, id='stock1', stock=100, reducible_quantity=100)

        self.assertEqual(adapter.add_to_cart(), 'URL')
        self.assertEqual(IStatusMessage().addStatusMessage.call_count, 6)
        self.assertEqual(IShoppingSite(article1).cart, {'articles': SessionArticles([(uuid1, {
            'sku': 'SKÖ1',
            'gross': Money(Decimal('12.40'), 'EUR'),
            'description': '',
            'weight': 0.0,
            'title': '',
            'url': 'http://nohost/plone/article1',
            'height': 0.0,
            'width': 0.0,
            'depth': 0.0,
            'vat_rate': Decimal('24.00'),
            'net': Money(Decimal('10.00'), 'EUR'),
            'id': uuid1,
            'vat': Money(Decimal('2.40'), 'EUR'),
            'quantity': 2,
        })])})
