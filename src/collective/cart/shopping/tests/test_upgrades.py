# -*- coding: utf-8 -*-
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

    @mock.patch('collective.cart.shopping.upgrades.getToolByName')
    def test_reimport_jsregistry(self, getToolByName):
        from collective.cart.shopping.upgrades import reimport_jsregistry
        reimport_jsregistry(self.portal)
        getToolByName().runImportStepFromProfile.assert_called_with(PROFILE_ID, 'jsregistry', run_dependencies=False, purge_old=False)

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

    def test_upgrade_14_to_15(self):
        article = self.create_content('collective.cart.core.Article', id='article',
            money=self.money('12.40'), vat=self.decimal('24.00'), vat_rate=24.0)
        del article.vat_rate

        self.assertEqual(article.vat, self.decimal('24.00'))
        with self.assertRaises(AttributeError):
            article.vat_rate

        shipping_method = self.create_atcontent('ShippingMethod', id='shipping-method')
        setattr(shipping_method, 'vat', '24.00')

        from collective.cart.shopping.upgrades import upgrade_14_to_15
        upgrade_14_to_15(self.portal)

        self.assertEqual(article.vat, self.decimal('24.00'))
        self.assertEqual(article.vat_rate, 24.0)
        self.assertEqual(shipping_method.vat, 24.0)

    def test_make_subarticles_private(self):
        from collective.cart.shopping.upgrades import make_subarticles_private
        wftool = getToolByName(self.portal, "portal_workflow")
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=24.0)
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'private')

        # make public
        wftool.doActionFor(article1, 'publish')
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'published')

        # make article1 use_subarticle
        article1.use_subarticle = True
        article11 = self.create_content('collective.cart.core.Article', parent=article1, title='Ärticle11', sku='SKÖ11', money=self.money('12.40'), vat_rate=24.0)
        article12 = self.create_content('collective.cart.core.Article', parent=article1, title='Ärticle12', sku='SKÖ12', money=self.money('12.40'), vat_rate=24.0)
        wftool.doActionFor(article11, 'publish')
        status = wftool.getStatusOf("simple_publication_workflow", article11)
        self.assertEqual(status['review_state'], 'published')
        wftool.doActionFor(article12, 'publish')
        status = wftool.getStatusOf("simple_publication_workflow", article12)
        self.assertEqual(status['review_state'], 'published')

        # upgrade
        make_subarticles_private(self.portal)
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'published')
        status = wftool.getStatusOf("simple_publication_workflow", article11)
        self.assertEqual(status['review_state'], 'published')
        status = wftool.getStatusOf("simple_publication_workflow", article12)
        self.assertEqual(status['review_state'], 'published')

        article111 = self.create_content('collective.cart.core.Article', parent=article11, title='Ärticle111', sku='SKÖ111', money=self.money('12.40'), vat_rate=24.0)
        article112 = self.create_content('collective.cart.core.Article', parent=article11, title='Ärticle112', sku='SKÖ112', money=self.money('12.40'), vat_rate=24.0)
        article113 = self.create_content('collective.cart.core.Article', parent=article11, title='Ärticle113', sku='SKÖ113', money=self.money('12.40'), vat_rate=24.0)
        wftool.doActionFor(article111, 'publish')
        wftool.doActionFor(article112, 'publish')

        # make private
        wftool.doActionFor(article1, 'retract')
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'private')

        # upgrade
        make_subarticles_private(self.portal)
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article11)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article12)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article111)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article112)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article113)
        self.assertEqual(status['review_state'], 'private')
