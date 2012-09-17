from Products.CMFCore.utils import getToolByName
from collective.cart.shopping.tests.base import IntegrationTestCase


class TestCase(IntegrationTestCase):
    """TestCase for Shop creation."""

    def setUp(self):
        self.portal = self.layer['portal']

    def create_shop(self):
        from plone.dexterity.utils import createContentInContainer
        from zope.lifecycleevent import modified
        shop = createContentInContainer(
            self.portal, 'collective.cart.shopping.Shop', id='shop',
            checkConstraints=False, title='Shop')
        modified(shop)
        return shop

    def test_cart_container_created(self):
        from collective.cart.core.interfaces import IShoppingSite
        shop = self.create_shop()