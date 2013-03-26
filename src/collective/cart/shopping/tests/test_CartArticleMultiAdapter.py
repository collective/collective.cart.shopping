# -*- coding: utf-8 -*-
from Testing import ZopeTestCase as ztc
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import ICartArticleMultiAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified

import mock


class CartArticleMultiAdapterTestCase(IntegrationTestCase):
    """TestCase for CartArticleMultiAdapter"""

    def setUp(self):
        from plone.app.testing import TEST_USER_ID
        from plone.app.testing import setRoles
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        ztc.utils.setupCoreSessions(self.layer['app'])

    def test_subclass(self):
        from five.grok import MultiAdapter
        from collective.cart.shopping.adapter.interface import CartArticleMultiAdapter
        self.assertTrue(issubclass(CartArticleMultiAdapter, MultiAdapter))
        from zope.interface import Interface
        self.assertTrue(issubclass(ICartArticleMultiAdapter, Interface))

    def test_adapts(self):
        from collective.cart.shopping.adapter.interface import CartArticleMultiAdapter
        from zope.interface import Interface
        self.assertEqual(CartArticleMultiAdapter.__component_adapts__, (Interface, Interface))

    def test_provides(self):
        from collective.cart.shopping.adapter.interface import CartArticleMultiAdapter
        self.assertEqual(getattr(CartArticleMultiAdapter, 'grokcore.component.directive.provides'), ICartArticleMultiAdapter)

    def create_adapter(self, carticle={}):
        return getMultiAdapter((self.portal, carticle), ICartArticleMultiAdapter)

    def create_article(self, parent=None, **kwargs):
        if parent is None:
            parent = self.portal
        article = createContentInContainer(parent, 'collective.cart.core.Article', checkConstraints=False, **kwargs)
        modified(article)
        return article

    def test_orig_article(self):
        adapter = self.create_adapter()
        with self.assertRaises(KeyError):
            adapter.orig_article

        article = self.create_article(id="article", money=Money(Decimal('12.40'), 'EUR'), vat_rate=Decimal('24.00'))
        uuid = IUUID(article)

        session = IShoppingSite(self.portal).getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'UUID': {'id': 'UUID'}}})

        with self.assertRaises(KeyError):
            adapter.orig_article

        session.set('collective.cart.core', {'articles': {uuid: {'id': uuid}}})

    @mock.patch('collective.cart.shopping.adapter.interface.IArticleAdapter')
    def test_image_url(self, IArticleAdapter):
        adapter = self.create_adapter({'id': 'UUID'})
        IArticleAdapter().image_url = 'IMAGE_URL'
        self.assertEqual(adapter.image_url, 'IMAGE_URL')

    def test_gross_subtotal(self):
        adapter = self.create_adapter({'id': 'UUID'})
        with self.assertRaises(KeyError):
            adapter.gross_subtotal

        adapter.article.update({'gross': Money(Decimal('12.40'), 'EUR')})
        with self.assertRaises(KeyError):
            adapter.gross_subtotal

        adapter.article.update({'quantity': 2})
        self.assertEqual(adapter.gross_subtotal, Money(Decimal('24.80'), 'EUR'))

    @mock.patch('collective.cart.shopping.adapter.interface.IStock')
    def test_quantity_max(self, IStock):
        adapter = self.create_adapter({'id': 'UUID'})
        IStock().stock = 100
        self.assertEqual(adapter.quantity_max, 100)

    @mock.patch('collective.cart.shopping.adapter.interface.IStock')
    def test_quantity_size(self, IStock):
        adapter = self.create_adapter({'id': 'UUID'})
        IStock().stock = 100
        self.assertEqual(adapter.quantity_size, 3)
