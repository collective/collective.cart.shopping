from Products.CMFCore.utils import getToolByName
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class TestCase(IntegrationTestCase):
    """TestCase for upgrade steps."""

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_update_typeinfo(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.core.Article')
        ctype.allowed_content_types = ('Image')
        self.assertEqual(ctype.allowed_content_types, ('Image'))

        from collective.cart.shopping.upgrades import update_typeinfo
        update_typeinfo(self.portal)

        self.assertEqual(ctype.allowed_content_types, ('Image',
            'collective.cart.core.Article', 'collective.cart.stock.Stock'))

    def test_upgrade_1_to_2(self):
        from collective.cart.shopping.interfaces import ISubArticle
        from plone.dexterity.utils import createContentInContainer
        from zope.lifecycleevent import modified
        from decimal import Decimal
        from moneyed import Money
        from datetime import datetime
        from datetime import timedelta

        folder = self.portal[self.portal.invokeFactory('Folder', 'folder')]
        folder.reindexObject()

        price1 = Decimal('20.00')
        discount1 = Decimal('10.00')
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        item1 = {
            'id': 'sa1',
            'description': 'Description of SubArticle1',
            'sku': '001',
            'salable': True,
            'price': price1,
            'vat': Decimal('23.00'),
            'money': Money(price1, currency=u'EUR'),
            'discount_enabled': True,
            'discount_price': discount1,
            'discount_money': Money(discount1, currency=u'EUR'),
            'discount_start': today,
            'discount_end': tomorrow,
            'reducible_quantity': 100,
            'weight': 100.0,
            'width': 10.0,
            'height': 5.0,
            'depth': 20.0,
        }
        subarticle1 = createContentInContainer(
            self.portal, 'collective.cart.shopping.SubArticle',
            checkConstraints=False, **item1)
        subarticle1.title = 'SubArticle1'
        modified(subarticle1)

        price2 = Decimal('50.00')
        discount2 = Decimal('30.00')
        item2 = {
            'id': 'sa2',
            'description':
            'Description of SubArticle2',
            'sku': '002',
            'salable': True,
            'price': price2,
            'vat': Decimal('9.00'),
            'money': Money(price2, currency=u'EUR'),
            'discount_enabled': True,
            'discount_price': discount2,
            'discount_money': Money(discount2, currency=u'EUR'),
            'discount_start': today,
            'discount_end': tomorrow,
            'reducible_quantity': 150,
            'weight': 50.0,
            'width': 1.0,
            'height': 2.0,
            'depth': 3.0,
        }
        subarticle2 = createContentInContainer(
            folder, 'collective.cart.shopping.SubArticle',
            checkConstraints=False, **item2)
        subarticle2.title = 'SubArticle2'
        modified(subarticle2)

        from collective.cart.shopping.upgrades import upgrade_1_to_2
        upgrade_1_to_2(self.portal)

        article1 = self.portal['sa1']
        self.assertFalse(ISubArticle.providedBy(article1))
        for key in item1.keys():
            self.assertEqual(getattr(article1, key), item1[key])

        article2 = self.portal['folder']['sa2']
        self.assertFalse(ISubArticle.providedBy(article2))
        for key in item2.keys():
            self.assertEqual(getattr(article2, key), item2[key])

    def test_update_catalog(self):
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

        from collective.cart.shopping.upgrades import update_catalog
        update_catalog(self.portal)

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
