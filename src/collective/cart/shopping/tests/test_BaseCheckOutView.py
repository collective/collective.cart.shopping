# -*- coding: utf-8 -*-
from Testing import ZopeTestCase as ztc
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.browser.template import BaseCheckOutView
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.uuid.interfaces import IUUID
from plone.dexterity.utils import createContentInContainer
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.lifecycleevent import modified
from zope.publisher.browser import TestRequest

import mock


class BaseCheckOutViewTestCase(IntegrationTestCase):
    """TestCase for BaseCheckOutView"""

    def setUp(self):
        ztc.utils.setupCoreSessions(self.layer['app'])
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_subclass(self):
        from collective.cart.core.browser.template import BaseCheckOutView as BaseBaseCheckOutView
        self.assertTrue(issubclass(BaseCheckOutView, BaseBaseCheckOutView))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseCheckOutView, 'martian.martiandirective.baseclass'))

    def test_layer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        self.assertEqual(getattr(BaseCheckOutView, 'grokcore.view.directive.layer'), ICollectiveCartShoppingLayer)

    def create_view(self):
        request = TestRequest()
        request.set = mock.Mock()
        directlyProvides(request, IAttributeAnnotatable)
        return BaseCheckOutView(self.portal, request)

    def create_article(self, **kwargs):
        article = createContentInContainer(self.portal, 'collective.cart.core.Article', checkConstraints=False, **kwargs)
        modified(article)
        return article

    def create_stock(self, parent, **kwargs):
        stock = createContentInContainer(parent, 'collective.cart.stock.Stock', checkConstraints=False, **kwargs)
        modified(stock)
        return stock

    def create_shipping_method_container(self):
        container = createContentInContainer(self.portal, 'collective.cart.shipping.ShippingMethodContainer',
            checkConstraints=False, id='shipping-method-container')
        modified(container)
        return container

    def create_shipping_method(self, container, **kwargs):
        shipping_method = container[container.invokeFactory('ShippingMethod', **kwargs)]
        shipping_method.reindexObject()
        return shipping_method

    def test_shopping_site(self):
        from collective.cart.shopping.adapter.interface import ShoppingSite
        instance = self.create_view()
        self.assertIsInstance(instance.shopping_site, ShoppingSite)

    def test_update(self):
        self.portal.absolute_url = mock.Mock(return_value='portal_url')
        instance = self.create_view()
        article1 = self.create_article(id='article1', money=Money(Decimal('12.40'), currency='EUR'), vat_rate=Decimal('24.00'))
        self.assertIsNone(instance.update())

        IArticleAdapter(article1).add_to_cart()
        shopping_site = IShoppingSite(self.portal)
        self.assertEqual(len(shopping_site.cart_articles), 1)
        self.assertEqual(instance.update(), 'portal_url/@@cart')
        self.assertEqual(len(shopping_site.cart_articles), 0)

        stock1 = self.create_stock(article1, id="stock1", stock=10, description="Description of Stöck1",
            money=Money(Decimal('1.00'), 'EUR'), title="Stöck1")
        IArticleAdapter(article1).add_to_cart()
        self.assertEqual(len(shopping_site.cart_articles), 1)
        self.assertIsNone(instance.update())
        self.assertEqual(len(shopping_site.cart_articles), 1)

        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_shipping_method_container()
        shipping_method = self.create_shipping_method(container, id='shipping-method')
        uuid = IUUID(shipping_method)
        self.assertEqual(instance.update(), 'portal_url/@@cart')
        self.assertEqual(len(shopping_site.cart_articles), 1)

        shopping_site.update_cart('shipping_method', {'id': uuid})
        self.assertIsNone(instance.update())
        self.assertEqual(len(shopping_site.cart_articles), 1)

        stock1.stock = 0
        modified(stock1)
        self.assertEqual(instance.update(), 'portal_url/@@cart')
        self.assertEqual(len(shopping_site.cart_articles), 0)
