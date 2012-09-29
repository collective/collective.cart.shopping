from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent import modified

import unittest


class IShoppingSiteTestCase(unittest.TestCase):
    """TestCase for collective.cart.shopping.interfaces.IShoppingSite"""

    def test_subclass(self):
        from collective.cart import core
        from collective.cart.shopping.interfaces import IShoppingSite
        self.assertTrue(issubclass(IShoppingSite, core.interfaces.IShoppingSite))

    def get_field(self, name):
        """Get field(attribute) based on name.

        :param name: Name of field(attribute).
        :type name: str"""
        from collective.cart.shopping.interfaces import IShoppingSite
        return IShoppingSite.get(name)

    def test_shipping_methods(self):
        self.assertEqual(self.get_field('shipping_methods').getDoc(),
            'List of shipping methods')

    def test_shipping_method(self):
        self.assertEqual(self.get_field('shipping_method').getDoc(),
            'Shipping method from cart')


class ShoppingSiteTestCase(IntegrationTestCase):
    """TestCase for ShoppingSite"""

    def setUp(self):
        from plone.app.testing import TEST_USER_ID
        from plone.app.testing import setRoles
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_subclass__ShoppingSite(self):
        from collective.cart import core
        from collective.cart.shopping.adapter.interface import ShoppingSite
        self.assertTrue(issubclass(ShoppingSite, core.adapter.interface.ShoppingSite))

    def create_shop(self):
        """Create shop."""
        shop = createContentInContainer(self.portal, 'collective.cart.shopping.Shop', id='shop',
            checkConstraints=False, title='Shop')
        modified(shop)
        return shop

    def test_shipping_methods__without_any_shipping_methods(self):
        from collective.cart.shopping.interfaces import IShoppingSite
        shop = self.create_shop()
        self.assertEqual(len(IShoppingSite(shop).shipping_methods), 0)

    def test_shipping_methods__with_shipping_method(self):
        from collective.cart.shopping.interfaces import IShoppingSite
        shop = self.create_shop()
        container = createContentInContainer(shop, 'collective.cart.shipping.ShippingMethodContainer',
            id='shipping-method-container', checkConstraints=False)
        sm = container[container.invokeFactory('ShippingMethod', 'shipping_method')]
        sm.reindexObject()
        self.assertEqual(IShoppingSite(shop).shipping_methods[0].UID, IUUID(sm))
