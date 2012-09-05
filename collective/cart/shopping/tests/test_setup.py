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

    def test_is_collective_cart_shipping_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.cart.shipping'))

    def test_is_collective_behavior_discount_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.discount'))

    def test_is_collective_behavior_size_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.size'))

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

    def get_record(self, name):
        """Get record by name.
        :param name: Name of record.
        :type name: basestring

        :rtype: plone.registry.record.Record
        """
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility
        return getUtility(IRegistry).records.get(name)

    def test_registry_record__collective_cart_shopping_number_of_images__field__instance(self):
        from plone.registry.field import Int
        record = self.get_record('collective.cart.shopping.number_of_images')
        self.assertIsInstance(record.field, Int)

    def test_registry_record__collective_cart_shopping_number_of_images__field__title(self):
        record = self.get_record('collective.cart.shopping.number_of_images')
        self.assertEqual(record.field.title, u'Number of Images')

    def test_registry_record__collective_cart_shopping_number_of_images__field__description(self):
        record = self.get_record('collective.cart.shopping.number_of_images')
        self.assertEqual(record.field.description, u'No more than this number of images can be added to one article.')

    def test_registry_record__collective_cart_shopping_number_of_images__field__min(self):
        record = self.get_record('collective.cart.shopping.number_of_images')
        self.assertEqual(record.field.min, 0)

    def test_registry_record__collective_cart_shopping_number_of_images__value(self):
        record = self.get_record('collective.cart.shopping.number_of_images')
        self.assertEqual(record.value, 3)

    def test_types__collective_cart_core_Article__i18n_domain(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.i18n_domain, 'collective.cart.shopping')

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
                'collective.behavior.vat.interfaces.IVAT',
                'collective.behavior.size.interfaces.ISize',
                'plone.app.relationfield.behavior.IRelatedItems'))

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

    def test_uninstall__registry(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.shopping'])
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility
        with self.assertRaises(KeyError):
            getUtility(IRegistry)['collective.cart.shopping.number_of_images']
