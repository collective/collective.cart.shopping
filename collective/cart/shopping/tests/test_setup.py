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

    def test_types__collective_cart_shopping_Shop__i18n_domain(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.i18n_domain, 'collective.cart.shopping')

    def test_types__collective_cart_shopping_Shop__meta_type(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.meta_type, 'Dexterity FTI')

    def test_types__collective_cart_shopping_Shop__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.title, 'Shop')

    def test_types__collective_cart_shopping_Shop__description(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.description, '')

    def test_types__collective_cart_shopping_Shop__content_icon(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.getIcon(), '++resource++collective.cart.shopping/shop.png')

    def test_types__collective_cart_shopping_Shop__allow_discussion(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertFalse(ctype.allow_discussion)

    def test_types__collective_cart_shopping_Shop__global_allow(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertTrue(ctype.global_allow)

    def test_types__collective_cart_shopping_Shop__filter_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertFalse(ctype.filter_content_types)

    def test_types__collective_cart_shopping_Shop__allowed_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.allowed_content_types, ())

    def test_types__collective_cart_shopping_Shop__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.schema, 'collective.cart.shopping.interfaces.IShop')

    def test_types__collective_cart_shopping_Shop__klass(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.klass, 'plone.dexterity.content.Container')

    def test_types__collective_cart_shopping_Shop__add_permission(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.add_permission, 'collective.cart.shopping.AddShop')

    def test_types__collective_cart_shopping_Shop__behaviors(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(
            ctype.behaviors,
            (
                'plone.app.content.interfaces.INameFromTitle',
                'plone.app.dexterity.behaviors.metadata.IDublinCore'))

    def test_types__collective_cart_shopping_Shop__default_view(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.default_view, 'view')

    def test_types__collective_cart_shopping_Shop__default_view_fallback(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertFalse(ctype.default_view_fallback)

    def test_types__collective_cart_shopping_Shop__view_methods(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.view_methods, ('view',))

    def test_types__collective_cart_shopping_Shop__default_aliases(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(
            ctype.default_aliases,
            {'edit': '@@edit', 'sharing': '@@sharing', '(Default)': '(dynamic view)', 'view': '(selected layout)'})

    def test_types__collective_cart_shopping_Shop__action__view__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.title, 'View')

    def test_types__collective_cart_shopping_Shop__action__view__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_shopping_Shop__action__view__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.getActionExpression(), 'string:${folder_url}/')

    def test_types__collective_cart_shopping_Shop__action__view__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/view')
        self.assertTrue(action.visible)

    def test_types__collective_cart_shopping_Shop__action__view__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.permissions, (u'View',))

    def test_types__collective_cart_shopping_Shop__action__edit__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.title, 'Edit')

    def test_types__collective_cart_shopping_Shop__action__edit__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_shopping_Shop__action__edit__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')

    def test_types__collective_cart_shopping_Shop__action__edit__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/edit')
        self.assertTrue(action.visible)

    def test_types__collective_cart_shopping_Shop__action__edit__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.permissions, (u'Modify portal content',))

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
