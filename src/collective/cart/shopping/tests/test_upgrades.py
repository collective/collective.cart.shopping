from Products.CMFCore.utils import getToolByName
from collective.cart.shopping.tests.base import IntegrationTestCase
from collective.cart.shopping.upgrades import PROFILE_ID

import mock


class TestCase(IntegrationTestCase):
    """TestCase for upgrade steps."""

    @mock.patch('collective.cart.shopping.upgrades.getToolByName')
    def test_reimport_rolemap(self, getToolByName):
        from collective.cart.shopping.upgrades import reimport_rolemap
        reimport_rolemap(self.portal)
        getToolByName().runImportStepFromProfile.assert_called_with(PROFILE_ID, 'rolemap', run_dependencies=False, purge_old=False)

    @mock.patch('collective.cart.shopping.upgrades.getToolByName')
    def test_reimport_propertiestool(self, getToolByName):
        from collective.cart.shopping.upgrades import reimport_propertiestool
        reimport_propertiestool(self.portal)
        getToolByName().runImportStepFromProfile.assert_called_with(PROFILE_ID, 'propertiestool', run_dependencies=False, purge_old=False)

    @mock.patch('collective.cart.shopping.upgrades.getToolByName')
    def test_reimport_viewlets(self, getToolByName):
        from collective.cart.shopping.upgrades import reimport_viewlets
        reimport_viewlets(self.portal)
        getToolByName().runImportStepFromProfile.assert_called_with(PROFILE_ID, 'viewlets', run_dependencies=False, purge_old=False)

    @mock.patch('collective.cart.shopping.upgrades.getToolByName')
    def test_reimport_registry(self, getToolByName):
        from collective.cart.shopping.upgrades import reimport_registry
        reimport_registry(self.portal)
        getToolByName().runImportStepFromProfile.assert_called_with(PROFILE_ID, 'plone.app.registry', run_dependencies=False, purge_old=False)

    def test_reimport_typeinfo(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        ctype.allowed_content_types = ('Image')
        self.assertEqual(ctype.allowed_content_types, ('Image'))

        from collective.cart.shopping.upgrades import reimport_typeinfo
        reimport_typeinfo(self.portal)

        self.assertEqual(ctype.allowed_content_types, ('Image',
            'collective.cart.core.Article', 'collective.cart.stock.Stock'))

    def test_reimport_catalog(self):
        from collective.cart.shopping.interfaces import ICustomerInfo
        from plone.dexterity.utils import createContentInContainer
        item = {
            "first_name": 'FIST NAME',
            "last_name": 'LAST NAME',
            "organization": 'ORGANIZATION',
            "vat": 'VAT',
            "email": 'EMAIL',
            "street": 'STREET',
            "post": 'POST',
            "city": 'CITY',
            "phone": 'PHONE',
        }
        createContentInContainer(self.portal, 'collective.cart.shopping.CustomerInfo',
            checkConstraints=False, **item)
        catalog = getToolByName(self.portal, 'portal_catalog')
        catalog.manage_catalogClear()
        self.assertEqual(len(catalog()), 0)
        column = 'first_name'
        catalog.delColumn(column)
        self.assertNotIn(column, catalog.schema())

        from collective.cart.shopping.upgrades import reimport_catalog
        reimport_catalog(self.portal)

        self.assertIn(column, catalog.schema())
        self.assertNotEqual(len(catalog()), 0)
        brain = catalog(object_provides=ICustomerInfo.__identifier__)[0]
        self.assertEqual(brain.first_name, 'FIST NAME')
        self.assertEqual(brain.last_name, 'LAST NAME')
        self.assertEqual(brain.organization, 'ORGANIZATION')
        self.assertEqual(brain.vat, 'VAT')
        self.assertEqual(brain.email, 'EMAIL')
        self.assertEqual(brain.street, 'STREET')
        self.assertEqual(brain.post, 'POST')
        self.assertEqual(brain.city, 'CITY')
        self.assertEqual(brain.phone, 'PHONE')

    def test_reimport_cssregistry(self):
        css = getToolByName(self.portal, 'portal_css')
        rid = '++resource++collective.cart.shopping/css/style.css'
        css.unregisterResource(rid)
        self.assertIsNone(css.getResource(rid))

        from collective.cart.shopping.upgrades import reimport_cssregistry
        reimport_cssregistry(self.portal)

        self.assertIsNotNone(css.getResource(rid))

    def test_reimport_actions(self):
        from collective.cart.core.tests.test_setup import get_action
        self.assertIsNotNone(get_action(self.portal, 'object', 'article-list'))

        category = getattr(getToolByName(self.portal, 'portal_actions'), 'object')
        category.manage_delObjects(['article-list'])

        with self.assertRaises(AttributeError):
            get_action(self.portal, 'object', 'article-list')

        from collective.cart.shopping.upgrades import reimport_actions
        reimport_actions(self.portal)

        self.assertIsNotNone(get_action(self.portal, 'object', 'article-list'))
