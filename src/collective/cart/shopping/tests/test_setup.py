from Products.CMFCore.utils import getToolByName
from collective.cart.core.tests.test_setup import get_action
from collective.cart.shopping.tests.base import IntegrationTestCase


class TestCase(IntegrationTestCase):
    """TestCase for Plone setup."""

    def test_is_package_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.cart.shopping'))

    def test_actions__object_stock__meta_type(self):
        action = get_action(self.portal, 'object', 'stock')
        self.assertEqual(action.meta_type, 'CMF Action')

    def test_actions__object_stock__i18n_domain(self):
        action = get_action(self.portal, 'object', 'stock')
        self.assertEqual(action.i18n_domain, 'collective.cart.shopping')

    def test_actions__object_stock__title(self):
        action = get_action(self.portal, 'object', 'stock')
        self.assertEqual(action.title, 'Stock')

    def test_actions__object_stock__description(self):
        action = get_action(self.portal, 'object', 'stock')
        self.assertEqual(action.description, '')

    def test_actions__object_stock__url_expr(self):
        action = get_action(self.portal, 'object', 'stock')
        self.assertEqual(
            action.url_expr, 'string:${globals_view/getCurrentFolderUrl}/@@stock')

    def test_actions__object_stock__available_expr(self):
        action = get_action(self.portal, 'object', 'stock')
        self.assertEqual(
            action.available_expr, 'python: object.restrictedTraverse("is-article")()')

    def test_actions__object_stock__permissions(self):
        action = get_action(self.portal, 'object', 'stock')
        self.assertEqual(action.permissions, ('Modify portal content',))

    def test_actions__object_stock__visible(self):
        action = get_action(self.portal, 'object', 'stock')
        self.assertTrue(action.visible)

    def test_browserlayer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        from plone.browserlayer import utils
        self.failUnless(ICollectiveCartShoppingLayer in utils.registered_layers())

    def test_catalog__column__gross(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('gross', catalog.schema())

    def test_catalog__column__quantity(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('quantity', catalog.schema())

    def test_catalog__column__first_name(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('first_name', catalog.schema())

    def test_catalog__column__last_name(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('last_name', catalog.schema())

    def test_catalog__column__organization(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('organization', catalog.schema())

    def test_catalog__column__vat(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('vat', catalog.schema())

    def test_catalog__column__email(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('email', catalog.schema())

    def test_catalog__column__street(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('street', catalog.schema())

    def test_catalog__column__post(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('post', catalog.schema())

    def test_catalog__column__city(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('city', catalog.schema())

    def test_catalog__column__phone(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('phone', catalog.schema())

    def test_catalog__index__use_subarticle(self):
        from Products.PluginIndexes.BooleanIndex.BooleanIndex import BooleanIndex
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIsInstance(catalog.Indexes['use_subarticle'], BooleanIndex)

    def test_jsregistry__check_out_buttons(self):
        javascripts = getToolByName(self.portal, 'portal_javascripts')
        resource = javascripts.getResource('++resource++collective.cart.shopping/javascript/check-out-buttons.js')
        self.assertFalse(resource.getAuthenticated())
        self.assertEqual(resource.getBundle(), 'default')
        self.assertTrue(resource.getCacheable())
        self.assertEqual(resource.getCompression(), 'safe')
        self.assertEqual(resource.getConditionalcomment(), '')
        self.assertTrue(resource.getCookable())
        self.assertTrue(resource.getEnabled())
        self.assertEqual(resource.getExpression(), "python: context.restrictedTraverse('@@is-check-out-view')()")
        self.assertFalse(resource.getInline())

    def test_metadata_dependency_collective_cart_core(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.cart.core'))

    def test_metadata_dependency_collective_cart_shipping(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.cart.shipping'))

    def test_metadata_dependency_collective_behavior_discount(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.discount'))

    def test_metadata_dependency_collective_behavior_size(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.size'))

    def test_metadata_dependency_collective_behavior_sku(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.sku'))

    def test_metadata_dependency_collective_behavior_stock(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.stock'))

    def test_metadata_dependency_collective_behavior_vat(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('collective.behavior.vat'))

    def test_metadata__version(self):
        setup = getToolByName(self.portal, 'portal_setup')
        self.assertEqual(
            setup.getVersionForProfile('profile-collective.cart.shopping:default'), u'19')

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

    def test_registry_record__collective_cart_shopping_notification_cc_email__field__instance(self):
        from plone.registry.field import TextLine
        record = self.get_record('collective.cart.shopping.notification_cc_email')
        self.assertIsInstance(record.field, TextLine)

    def test_registry_record__collective_cart_shopping_notification_cc_email__field__title(self):
        record = self.get_record('collective.cart.shopping.notification_cc_email')
        self.assertEqual(record.field.title, u'Notification CC E-mail')

    def test_registry_record__collective_cart_shopping_notification_cc_email__field__description(self):
        record = self.get_record('collective.cart.shopping.notification_cc_email')
        self.assertEqual(record.field.description, u'CC of e-mail sent to customers.')

    def test_registry_record__collective_cart_shopping_notification_cc_email__value(self):
        record = self.get_record('collective.cart.shopping.notification_cc_email')
        self.assertIsNone(record.value)

    def test_rolemap__collective_cart_shipping_AddShop__rolesOfPermission(self):
        permission = "collective.cart.shopping: Add Shop"
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        roles.sort()
        self.assertEqual(roles, [
            'Manager',
            'Site Administrator'])

    def test_rolemap__collective_cart_shipping_AddShop__acquiredRolesAreUsedBy(self):
        permission = "collective.cart.shopping: Add Shop"
        self.assertEqual(
            self.portal.acquiredRolesAreUsedBy(permission), '')

    def test_rolemap__collective_cart_shipping_AddArticleContainer__rolesOfPermission(self):
        permission = "collective.cart.shopping: Add Article Container"
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        roles.sort()
        self.assertEqual(roles, [
            'Contributor',
            'Manager',
            'Site Administrator'])

    def test_rolemap__collective_cart_shipping_AddArticleContainer__acquiredRolesAreUsedBy(self):
        permission = "collective.cart.shopping: Add Article Container"
        self.assertEqual(
            self.portal.acquiredRolesAreUsedBy(permission), '')

    def test_site_properties__types_not_searchable(self):
        properties = getToolByName(self.portal, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        contents = (
            'collective.cart.shipping.ShippingMethodContainer',
            'collective.cart.shopping.ArticleContainer',
            'collective.cart.shopping.CustomerInfo',
            'collective.cart.stock.Stock')
        for content in contents:
            self.assertIn(content, site_properties.getProperty('types_not_searched'))

    def test_navtree_properties__metaTypesNotToList(self):
        properties = getToolByName(self.portal, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        contents = (
            'collective.cart.shipping.ShippingMethodContainer',
            'collective.cart.shopping.CustomerInfo',
            'collective.cart.stock.Stock')
        for content in contents:
            self.assertIn(content, navtree_properties.getProperty('metaTypesNotToList'))

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
        self.assertEqual(ctype.allowed_content_types, (
            'Image', 'collective.cart.core.Article', 'collective.cart.stock.Stock'))

    def test_types__collective_cart_core_Article__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.schema, 'collective.cart.shopping.schema.ArticleSchema')

    def test_types__collective_cart_core_Article__behaviors(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        self.assertEqual(ctype.behaviors, (
            'plone.app.content.interfaces.INameFromTitle',
            'plone.app.dexterity.behaviors.metadata.IDublinCore',
            'collective.behavior.sku.interfaces.ISKU',
            'collective.behavior.salable.interfaces.ISalable',
            'collective.behavior.discount.interfaces.IDiscount',
            'collective.behavior.stock.interfaces.IStock',
            'collective.behavior.vat.interfaces.IVAT',
            'collective.behavior.size.interfaces.ISize'))

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
        self.assertTrue(ctype.filter_content_types)

    def test_types__collective_cart_shopping_Shop__allowed_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.allowed_content_types, (
            'Folder',
            'collective.cart.shopping.ArticleContainer'))

    def test_types__collective_cart_shopping_Shop__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.schema, 'collective.cart.shopping.schema.ShopSchema')

    def test_types__collective_cart_shopping_Shop__klass(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.Shop')
        self.assertEqual(ctype.klass, 'collective.cart.shopping.content.Shop')

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

    def test_types__collective_cart_shopping_ArticleContainer__i18n_domain(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.i18n_domain, 'collective.cart.shopping')

    def test_types__collective_cart_shopping_ArticleContainer__meta_type(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.meta_type, 'Dexterity FTI')

    def test_types__collective_cart_shopping_ArticleContainer__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.title, 'Article Container')

    def test_types__collective_cart_shopping_ArticleContainer__description(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.description, '')

    def test_types__collective_cart_shopping_ArticleContainer__content_icon(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.getIcon(), '++resource++collective.cart.shopping/article-container.png')

    def test_types__collective_cart_shopping_ArticleContainer__allow_discussion(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertFalse(ctype.allow_discussion)

    def test_types__collective_cart_shopping_ArticleContainer__global_allow(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertTrue(ctype.global_allow)

    def test_types__collective_cart_shopping_ArticleContainer__filter_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertTrue(ctype.filter_content_types)

    def test_types__collective_cart_shopping_ArticleContainer__allowed_content_types(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.allowed_content_types, ('Folder', 'Image',
            'collective.cart.core.Article',
            'collective.cart.shopping.ArticleContainer'))

    def test_types__collective_cart_shopping_ArticleContainer__schema(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.schema, 'collective.cart.shopping.schema.ArticleContainerSchema')

    def test_types__collective_cart_shopping_ArticleContainer__klass(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.klass, 'collective.cart.shopping.content.ArticleContainer')

    def test_types__collective_cart_shopping_ArticleContainer__add_permission(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.add_permission, 'collective.cart.shopping.AddArticleContainer')

    def test_types__collective_cart_shopping_ArticleContainer__behaviors(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(
            ctype.behaviors,
            (
                'plone.app.content.interfaces.INameFromTitle',
                'plone.app.dexterity.behaviors.metadata.IDublinCore',
                'plone.app.dexterity.behaviors.exclfromnav.IExcludeFromNavigation'))

    def test_types__collective_cart_shopping_ArticleContainer__default_view(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.default_view, 'view')

    def test_types__collective_cart_shopping_ArticleContainer__default_view_fallback(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertFalse(ctype.default_view_fallback)

    def test_types__collective_cart_shopping_ArticleContainer__view_methods(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(ctype.view_methods, ('view',))

    def test_types__collective_cart_shopping_ArticleContainer__default_aliases(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        self.assertEqual(
            ctype.default_aliases,
            {'edit': '@@edit', 'sharing': '@@sharing', '(Default)': '(dynamic view)', 'view': '(selected layout)'})

    def test_types__collective_cart_shopping_ArticleContainer__action__view__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.title, 'View')

    def test_types__collective_cart_shopping_ArticleContainer__action__view__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_shopping_ArticleContainer__action__view__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.getActionExpression(), 'string:${folder_url}/')

    def test_types__collective_cart_shopping_ArticleContainer__action__view__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/view')
        self.assertTrue(action.visible)

    def test_types__collective_cart_shopping_ArticleContainer__action__view__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/view')
        self.assertEqual(action.permissions, (u'View',))

    def test_types__collective_cart_shopping_ArticleContainer__action__edit__title(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.title, 'Edit')

    def test_types__collective_cart_shopping_ArticleContainer__action__edit__condition(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.condition, '')

    def test_types__collective_cart_shopping_ArticleContainer__action__edit__url_expr(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')

    def test_types__collective_cart_shopping_ArticleContainer__action__edit__visible(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/edit')
        self.assertTrue(action.visible)

    def test_types__collective_cart_shopping_ArticleContainer__action__edit__permissions(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.ArticleContainer')
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.permissions, (u'Modify portal content',))

    def test_viewlets__order__collective_base_viewlet_manager_base_form(self):
        from zope.component import getUtility
        from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
        storage = getUtility(IViewletSettingsStorage)
        manager = "collective.base.viewlet-manager.base-form"
        skinname = "*"
        for viewlet in (
            u'collective.cart.core.viewlet.add-to-cart',
            u'collective.cart.shopping.viewlet.body-text',
            u'collective.cart.shopping.viewlet.articles-in-article',
            u'collective.cart.shopping.viewlet.add-subtract-stock',
            u'collective.cart.shopping.viewlet.stock-listing',
            u'collective.cart.core.viewlet.cart-article-listing',
            u'collective.cart.shopping.viewlet.cart-articles-total',
            u'collective.cart.shopping.viewlet.cart-check-out-buttons',
            u'collective.cart.shopping.viewlet.billing-and-shipping-billing-address',
            u'collective.cart.shopping.viewlet.billing-and-shipping-shipping-address',
            u'collective.cart.shopping.viewlet.billing-and-shipping-shipping-methods',
            u'collective.cart.shopping.viewlet.billing-and-shipping-check-out-buttons',
            u'collective.cart.shopping.viewlet.order-confirmation-cart-article-listing',
            u'collective.cart.shopping.viewlet.order-confirmation-shipping-method',
            u'collective.cart.shopping.viewlet.order-confirmation-total',
            u'collective.cart.shopping.viewlet.order-confirmation-terms',
            u'collective.cart.shopping.viewlet.order-confirmation-check-out-buttons'):
            self.assertIn(viewlet, storage.getOrder(manager, skinname))

    # def test_viewlets__hidden__plone_belowcontenttitle(self):
    #     from zope.component import getUtility
    #     from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
    #     storage = getUtility(IViewletSettingsStorage)
    #     manager = "plone.belowcontenttitle"
    #     skinname = "*"
    #     for viewlet in (u'collective.cart.core.viewlet.add-to-cart',):
    #         self.assertIn(viewlet, storage.getHidden(manager, skinname))

    def test_viewlets__hidden__plone_abovecontent(self):
        from zope.component import getUtility
        from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
        storage = getUtility(IViewletSettingsStorage)
        manager = "plone.abovecontent"
        skinname = "*"
        for viewlet in (u'collective.cart.shipping.shipping.method',):
            self.assertIn(viewlet, storage.getHidden(manager, skinname))

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

    def test_uninstall__registry__record__collective_cart_shopping_number_of_images(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.shopping'])
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility
        with self.assertRaises(KeyError):
            getUtility(IRegistry)['collective.cart.shopping.number_of_images']

    def test_uninstall__registry__record__collective_cart_shopping_notification_cc_email(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.cart.shopping'])
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility
        with self.assertRaises(KeyError):
            getUtility(IRegistry)['collective.cart.shopping.notification_cc_email']
