from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent import modified

import unittest


class ICartAdapterTestCase(unittest.TestCase):
    """TestCase for collective.cart.shopping.interfaces.ICartAdapter"""

    def test_subclass(self):
        from collective.cart import core
        from collective.cart.shopping.interfaces import ICartAdapter
        self.assertTrue(issubclass(ICartAdapter, core.interfaces.ICartAdapter))

    def get_field(self, name):
        """Get field(attribute) based on name.

        :param name: Name of field(attribute).
        :type name: str"""
        from collective.cart.shopping.interfaces import ICartAdapter
        return ICartAdapter.get(name)

    def test_shipping_method(self):
        self.assertEqual(self.get_field('shipping_method').getDoc(),
            'Brain of shipping method')

    def test_shipping_gross_money(self):
        self.assertEqual(self.get_field('shipping_gross_money').getDoc(),
            'Gross money of shipping method')

    def test_shipping_net_money(self):
        self.assertEqual(self.get_field('shipping_net_money').getDoc(),
            'Net money of shipping method')

    def test_shipping_vat_money(self):
        self.assertEqual(self.get_field('shipping_vat_money').getDoc(),
            'VAT money of shipping method')


class CartAdapterTestCase(IntegrationTestCase):
    """TestCase for CartAdapter."""

    def setUp(self):
        from plone.app.testing import TEST_USER_ID
        from plone.app.testing import setRoles
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_subclass__CartAdapter(self):
        from collective.cart import core
        from collective.cart.shopping.adapter.cart import CartAdapter
        self.assertTrue(issubclass(CartAdapter, core.adapter.cart.CartAdapter))

    def create_shop(self):
        """Create shop."""
        shop = createContentInContainer(self.portal, 'collective.cart.shopping.Shop', id='shop',
            checkConstraints=False, title='Shop')
        modified(shop)
        return shop

    def create_cart(self, shop=None):
        """Create cart."""
        if shop is None:
            # Create shop.
            shop = createContentInContainer(self.portal, 'collective.cart.shopping.Shop', id='shop',
                checkConstraints=False, title='Shop')
            modified(shop)
        # Cart container is created with event subscriber.
        cart_container = shop['cart-container']
        # Create cart.
        cart = createContentInContainer(cart_container, 'collective.cart.core.Cart', id='1',
            checkConstraints=False)
        modified(cart)
        return cart

    def test_instance(self):
        from collective.cart.shopping.adapter.cart import CartAdapter
        from collective.cart.shopping.interfaces import ICartAdapter
        cart = self.create_cart()
        self.assertIsInstance(ICartAdapter(cart), CartAdapter)

    def test_shipping_method__None(self):
        """Test cart containing no shipping methods."""
        from collective.cart.shopping.interfaces import ICartAdapter
        cart = self.create_cart()
        self.assertIsNone(ICartAdapter(cart).shipping_method)

    def test_shipping_method(self):
        """Test cart containing a shipping method."""
        from collective.cart.shopping.interfaces import ICartAdapter
        cart = self.create_cart()
        shipping_method = createContentInContainer(cart, 'collective.cart.shipping.CartShippingMethod',
            id='shippingmethod1', checkConstraints=False)
        modified(shipping_method)
        self.assertEqual(ICartAdapter(cart).shipping_method.UID, IUUID(shipping_method))

    def test_update_shipping_method__without_any_shipping_methods(self):
        """Test method: update_shopping_method even if there are no shipping methods available."""
        from collective.cart.shopping.interfaces import ICartAdapter
        cart = self.create_cart()
        ICartAdapter(cart).update_shipping_method()
        self.assertIsNone(ICartAdapter(cart).shipping_method)

    def create_articles(self, cart):
        article1 = createContentInContainer(cart, 'collective.cart.core.CartArticle',
            id='article1', weight=100.0, quantity=1, gross=Money(10.0, currency=u'EUR'), orig_uuid='UUID')
        modified(article1)
        article2 = createContentInContainer(cart, 'collective.cart.core.CartArticle',
            id='article2', weight=200.0, quantity=2, gross=Money(20.0, currency=u'EUR'), orig_uuid='UUID')
        modified(article2)
        return (article1, article2)

    def test__calculated_weight(self):
        from collective.cart.shopping.interfaces import ICartAdapter
        cart = self.create_cart()
        self.create_articles(cart)
        self.assertEqual(ICartAdapter(cart)._calculated_weight(), 0.5)

    def test_shipping_gross_money__without_shipping_method(self):
        from collective.cart.shopping.interfaces import ICartAdapter
        cart = self.create_cart()
        self.assertIsNone(ICartAdapter(cart).shipping_gross_money)

    def create_shipping_methods(self, shop):
        shipping_method_container = createContentInContainer(shop, 'collective.cart.shipping.ShippingMethodContainer',
            id='shipping-method-container', checkConstraints=False)
        modified(shipping_method_container)
        shippingmethod1 = shipping_method_container[shipping_method_container.invokeFactory(
            'ShippingMethod', 'shippingmethod1', title='ShippingMethod1',
            min_delivery_days=5, max_delivery_days=10, vat=Decimal('10.00'))]
        shippingmethod1.reindexObject()
        shippingmethod2 = shipping_method_container[shipping_method_container.invokeFactory(
            'ShippingMethod', 'shippingmethod2', title='ShippingMethod2',
            min_delivery_days=1, max_delivery_days=2, vat=Decimal('20.00'))]
        shippingmethod2.reindexObject()
        return (shippingmethod1, shippingmethod2)

    def create_shipping_method(self, cart, orig_uuid):
        shipping_method = createContentInContainer(cart, 'collective.cart.shipping.CartShippingMethod',
            id='cart-shipping-method', orig_uuid=orig_uuid, checkConstraints=False,
            vat_rate=Decimal('10.00'))
        modified(shipping_method)
        return shipping_method

    def test_shipping_gross_money__with_shipping_method(self):
        from collective.cart.shopping.interfaces import ICartAdapter
        shop = self.create_shop()
        cart = self.create_cart(shop=shop)
        self.create_articles(cart)
        shipping_methods = self.create_shipping_methods(shop)
        self.create_shipping_method(cart, IUUID(shipping_methods[0]))
        self.assertEqual(ICartAdapter(cart).shipping_gross_money, Money(0.50, currency='EUR'))
        self.assertEqual(ICartAdapter(cart).shipping_net_money, Money(0.45, currency='EUR'))
        self.assertEqual(ICartAdapter(cart).shipping_vat_money, Money(0.05, currency='EUR'))

    def test_update_shipping_method(self):
        """Test method: update_shipping_method."""
        from collective.cart.shopping.interfaces import ICartAdapter
        shop = self.create_shop()
        shipping_methods = self.create_shipping_methods(shop)
        cart = self.create_cart(shop)
        self.create_articles(cart)
        ICartAdapter(cart).update_shipping_method()
        shipping_method = ICartAdapter(cart).shipping_method
        sm = [sm for sm in shipping_methods if IUUID(sm) == shipping_method.orig_uuid][0]
        self.assertEqual(shipping_method.Title, sm.Title())
        self.assertEqual(shipping_method.min_delivery_days, sm.min_delivery_days)
        self.assertEqual(shipping_method.max_delivery_days, sm.max_delivery_days)
        self.assertEqual(shipping_method.vat_rate, sm.vat)
        self.assertEqual(ICartAdapter(cart).shipping_gross_money, Money(0.50, currency='EUR'))
        self.assertEqual(ICartAdapter(cart).shipping_net_money, Money(0.45, currency='EUR'))
        self.assertEqual(ICartAdapter(cart).shipping_vat_money, Money(0.05, currency='EUR'))

        # Add another article to cart.
        article3 = createContentInContainer(cart, 'collective.cart.core.CartArticle',
            id='article3', weight=300.0, quantity=3, gross=Money(30.0, currency=u'EUR'), orig_uuid='UUID')
        modified(article3)

        # Update shipping method.
        ICartAdapter(cart).update_shipping_method()
        self.assertEqual(ICartAdapter(cart).shipping_gross_money, Money(1.40, currency='EUR'))
        self.assertEqual(ICartAdapter(cart).shipping_net_money, Money(1.26, currency='EUR'))
        self.assertEqual(ICartAdapter(cart).shipping_vat_money, Money(0.14, currency='EUR'))

        self.assertEqual(shipping_methods[1].Title(), 'ShippingMethod2')
        ICartAdapter(cart).update_shipping_method(uuid=IUUID(shipping_methods[1]))
        shipping_method = ICartAdapter(cart).shipping_method
        sm = [sm for sm in shipping_methods if IUUID(sm) == shipping_method.orig_uuid][0]
        self.assertEqual(shipping_method.Title, sm.Title())
        self.assertEqual(shipping_method.min_delivery_days, sm.min_delivery_days)
        self.assertEqual(shipping_method.max_delivery_days, sm.max_delivery_days)
        self.assertEqual(shipping_method.vat_rate, sm.vat)
        self.assertEqual(ICartAdapter(cart).shipping_gross_money, Money(1.40, currency='EUR'))
        self.assertEqual(ICartAdapter(cart).shipping_net_money, Money(1.12, currency='EUR'))
        self.assertEqual(ICartAdapter(cart).shipping_vat_money, Money(0.28, currency='EUR'))
