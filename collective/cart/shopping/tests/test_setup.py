from Products.CMFCore.utils import getToolByName
from collective.cart.shopping.tests.base import IntegrationTestCase


class TestCase(IntegrationTestCase):
    """TestCase for Plone setup."""

    def setUp(self):
        self.portal = self.layer['portal']

    def test_is_sll_shopping_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.cart.shopping'))

    def test_is_collective_cart_core_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.cart.core'))

    def test_is_collective_behavior_discount_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.discount'))

    def test_is_collective_behavior_stock_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.stock'))

    def test_is_collective_behavior_vat_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.vat'))

    def test_browserlayer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        from plone.browserlayer import utils
        self.failUnless(ICollectiveCartShoppingLayer in utils.registered_layers())

    def test_types__collective_cart_core_Article__i18n_domain(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.i18n_domain, 'collective.cart.core')

    def test_types__collective_cart_core_Article__global_allow(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertTrue(ctype.global_allow)

    def test_types__collective_cart_core_Article__allowed_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.allowed_content_types, ('Image', 'collective.cart.stock.Stock'))

    def test_types__collective_cart_core_Article__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.schema, 'collective.cart.shopping.interfaces.IArticle')

    def test_types__collective_cart_core_Article__behaviors(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(
            ctype.behaviors,
            (
                'plone.app.content.interfaces.INameFromTitle',
                'plone.app.dexterity.behaviors.metadata.IDublinCore',
                'collective.behavior.salable.interfaces.ISalable',
                'collective.behavior.discount.interfaces.IDiscount',
                'collective.behavior.stock.interfaces.IStock',
                'collective.behavior.vat.interfaces.IVAT'))

    def test_uninstall__package(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.shopping'])
        self.failIf(installer.isProductInstalled('collective.cart.shopping'))

    def test_uninstall__browserlayer(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.shopping'])
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        from plone.browserlayer import utils
        self.failIf(ICollectiveCartShoppingLayer in utils.registered_layers())
