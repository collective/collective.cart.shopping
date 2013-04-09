# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.adapter.interface import ShoppingSite
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from zope.interface import alsoProvides
from zope.lifecycleevent import modified


class ShoppingSiteTestCase(IntegrationTestCase):
    """TestCase for ShoppingSite"""

    def test_subclass(self):
        from collective.cart.core.adapter.interface import ShoppingSite as BaseShoppingSite
        self.assertTrue(issubclass(ShoppingSite, BaseShoppingSite))
        from collective.cart.core.interfaces import IShoppingSite as IBaseShoppingSite
        self.assertTrue(issubclass(IShoppingSite, IBaseShoppingSite))

    def test_provides(self):
        from collective.cart.shopping.adapter.interface import ShoppingSite
        self.assertEqual(getattr(ShoppingSite, 'grokcore.component.directive.provides'), IShoppingSite)

    def test_articles_total(self):
        adapter = IShoppingSite(self.portal)
        self.assertEqual(adapter.articles_total, self.money('0.00'))

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {
            '1': {'gross': self.money('10.00'), 'quantity': 2, 'vat_rate': 24.0}
        }})
        self.assertEqual(adapter.articles_total, self.money('20.00'))
        session.set('collective.cart.core', {'articles': {
            '1': {'gross': self.money('10.00'), 'quantity': 2, 'vat_rate': 24.0},
            '2': {'gross': self.money('5.00'), 'quantity': 4, 'vat_rate': 24.0},
        }})
        self.assertEqual(adapter.articles_total, self.money('40.00'))

    def test_shipping_methods(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_methods)

        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id='shipping-method-container')
        self.create_atcontent('ShippingMethod', container, id='shippingmethod1')
        self.assertIsNone(adapter.shipping_methods)

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertEqual(len(adapter.shipping_methods), 1)

    def test_shipping_method(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_method)

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'shipping_method': 'SHIPPINIG_METHOD'})
        self.assertEqual(adapter.shipping_method, 'SHIPPINIG_METHOD')

    def test__calculated_weight(self):
        adapter = IShoppingSite(self.portal)
        self.assertEqual(adapter._calculated_weight(), 0.0)

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'shipping_method': 'SHIPPINIG_METHOD'})
        self.assertEqual(adapter._calculated_weight(), 0.0)

        self.assertEqual(adapter._calculated_weight('RATE'), 0.0)

        self.assertEqual(adapter._calculated_weight(10.0), 0.0)

        cart = session.get('collective.cart.core')
        cart.update({'articles': {
            '1': {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1, 'vat_rate': 24.0}
        }})
        session.set('collective.cart.core', cart)
        self.assertEqual(adapter._calculated_weight(10.0), 0.1)

        cart.update({'articles': {
            '1': {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1, 'vat_rate': 24.0},
            '2': {'weight': 10.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1, 'vat_rate': 24.0},
        }})
        self.assertEqual(adapter._calculated_weight(10.0), 0.16)

        cart.update({'articles': {
            '1': {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 2, 'vat_rate': 24.0}
        }})
        self.assertEqual(adapter._calculated_weight(10.0), 0.2)

    def test_get_shipping_gross_money(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.get_shipping_gross_money('UUID'))

        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id='shipping-method-container')
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1')
        uuid1 = IUUID(shippingmethod1)
        session = adapter.getSessionData(create=True)

        session.set('collective.cart.core', {'shipping_method': {'uuid': uuid1}})
        self.assertIsNone(adapter.get_shipping_gross_money(uuid1))

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertEqual(adapter.get_shipping_gross_money(uuid1), self.money('0.00'))
        cart = session.get('collective.cart.core')
        cart.update({'articles': {
            '1': {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1, 'vat_rate': 24.0}
        }})
        session.set('collective.cart.core', cart)
        self.assertEqual(adapter.get_shipping_gross_money(uuid1), self.money('1.50'))

    def test_shipping_gross_money(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_gross_money)

        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id='shipping-method-container')
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1')
        uuid1 = IUUID(shippingmethod1)
        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'shipping_method': {'uuid': 'UUID'}})
        self.assertIsNone(adapter.shipping_gross_money)

        session.set('collective.cart.core', {'shipping_method': {'uuid': uuid1}})
        self.assertIsNone(adapter.shipping_gross_money)

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertEqual(adapter.shipping_gross_money, self.money('0.00'))

        cart = session.get('collective.cart.core')
        cart.update({'articles': {
            '1': {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1, 'vat_rate': 24.0}
        }})
        session.set('collective.cart.core', cart)
        self.assertEqual(adapter.shipping_gross_money, self.money('1.50'))

        shippingmethod1.setShipping_fee('return 2.0')
        self.assertEqual(adapter.shipping_gross_money, self.money('2.00'))

    def test_shipping_vat_money(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_vat_money)

        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id='shipping-method-container')
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1')
        uuid1 = IUUID(shippingmethod1)
        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {
            'shipping_method': {'uuid': uuid1, 'vat_rate': self.decimal('24.00')},
            'articles': {'1': {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1, 'vat_rate': 24.0}},
        })
        self.assertEqual(adapter.shipping_vat_money, self.money('0.36'))

    def test_shipping_net_money(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_net_money)

        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id='shipping-method-container')
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1')
        uuid1 = IUUID(shippingmethod1)
        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {
            'shipping_method': {'uuid': uuid1, 'vat_rate': self.decimal('24.00')},
            'articles': {'1': {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1, 'vat_rate': 24.0}},
        })
        self.assertEqual(adapter.shipping_net_money, self.money('1.14'))

    def test_total(self):
        adapter = IShoppingSite(self.portal)
        self.assertEqual(adapter.total, self.money('0.00'))

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {
            '1': {'gross': self.money('10.00'), 'quantity': 2, 'vat_rate': 24.0}
        }})
        self.assertEqual(adapter.total, self.money('20.00'))

        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id='shipping-method-container')
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1')
        uuid1 = IUUID(shippingmethod1)
        session.set('collective.cart.core', {
            'shipping_method': {'uuid': uuid1},
            'articles': {'1': {'gross': self.money('10.00'), 'quantity': 2, 'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'vat_rate': 24.0}},
        })
        self.assertEqual(adapter.total, self.money('23.00'))

    def test_update_shipping_method(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_method)

        adapter.update_shipping_method()
        self.assertIsNone(adapter.shipping_method)

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {
            '1': {'gross': self.money('10.00'), 'quantity': 2, 'vat_rate': 24.0}
        }})
        adapter.update_shipping_method()
        self.assertIsNone(adapter.shipping_method)

        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_content('collective.cart.shipping.ShippingMethodContainer', id='shipping-method-container')
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1', vat=self.decimal('24.00'))
        uuid1 = IUUID(shippingmethod1)
        adapter.update_shipping_method()
        self.assertEqual(adapter.shipping_method, {
            'gross': None,
            'max_delivery_days': None,
            'uuid': uuid1,
            'title': '',
            'min_delivery_days': None,
            'vat_rate': self.decimal('24.00'),
            'net': None,
            'vat': None,
            'weight_dimension_rate': 250.0
        })

        articles = {'1': {'gross': self.money('10.00'), 'quantity': 2, 'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'vat_rate': 24.0}}
        adapter.update_cart('articles', articles)
        adapter.update_shipping_method()

        self.assertEqual(adapter.shipping_method, {
            'gross': self.money('3.00'),
            'max_delivery_days': None,
            'uuid': uuid1,
            'title': '',
            'min_delivery_days': None,
            'vat_rate': self.decimal('24.00'),
            'net': self.money('2.28'),
            'vat': self.money('0.72'),
            'weight_dimension_rate': 250.0
        })

        articles = {'1': {'gross': self.money('10.00'), 'quantity': 4, 'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'vat_rate': 24.0}}
        adapter.update_cart('articles', articles)
        adapter.update_shipping_method(uuid1)
        self.assertEqual(adapter.shipping_method, {
            'gross': self.money('6.00'),
            'max_delivery_days': None,
            'uuid': uuid1,
            'title': '',
            'min_delivery_days': None,
            'vat_rate': self.decimal('24.00'),
            'net': self.money('4.56'),
            'vat': self.money('1.44'),
            'weight_dimension_rate': 250.0
        })

        articles = {'1': {'gross': self.money('10.00'), 'quantity': 2, 'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'vat_rate': 24.0}}
        adapter.update_cart('articles', articles)
        adapter.update_shipping_method('UUID')
        self.assertEqual(adapter.shipping_method, {
            'gross': self.money('3.00'),
            'max_delivery_days': None,
            'uuid': uuid1,
            'title': '',
            'min_delivery_days': None,
            'vat_rate': self.decimal('24.00'),
            'net': self.money('2.28'),
            'vat': self.money('0.72'),
            'weight_dimension_rate': 250.0
        })

        articles = {'1': {'gross': self.money('10.00'), 'quantity': 4, 'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'vat_rate': 24.0}}
        adapter.update_cart('articles', articles)
        adapter.update_shipping_method(uuid1)
        self.assertEqual(adapter.shipping_method, {
            'gross': self.money('6.00'),
            'max_delivery_days': None,
            'uuid': uuid1,
            'title': '',
            'min_delivery_days': None,
            'vat_rate': self.decimal('24.00'),
            'net': self.money('4.56'),
            'vat': self.money('1.44'),
            'weight_dimension_rate': 250.0
        })

        shippingmethod2 = self.create_atcontent('ShippingMethod', container, id='shippingmethod2', vat=self.decimal('24.00'), weight_dimension_rate=1.0)
        uuid2 = IUUID(shippingmethod2)
        articles = {'1': {'gross': self.money('10.00'), 'quantity': 2, 'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'vat_rate': 24.0}}
        adapter.update_cart('articles', articles)
        adapter.update_shipping_method(uuid2)
        self.assertEqual(adapter.shipping_method, {
            'gross': self.money('0.20'),
            'max_delivery_days': None,
            'uuid': uuid2,
            'title': '',
            'min_delivery_days': None,
            'vat_rate': self.decimal('24.00'),
            'net': self.money('0.15'),
            'vat': self.money('0.05'),
            'weight_dimension_rate': 1.0
        })

        articles = {'1': {'gross': self.money('10.00'), 'quantity': 4, 'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'vat_rate': 24.0}}
        adapter.update_cart('articles', articles)
        adapter.update_shipping_method(uuid1)
        self.assertEqual(adapter.shipping_method, {
            'gross': self.money('6.00'),
            'max_delivery_days': None,
            'uuid': uuid1,
            'title': '',
            'min_delivery_days': None,
            'vat_rate': self.decimal('24.00'),
            'net': self.money('4.56'),
            'vat': self.money('1.44'),
            'weight_dimension_rate': 250.0
        })

        adapter.remove_from_cart('shipping_method')
        self.assertIsNone(adapter.shipping_method)
        adapter.update_shipping_method(uuid1)
        self.assertEqual(adapter.shipping_method, {
            'gross': self.money('6.00'),
            'max_delivery_days': None,
            'uuid': uuid1,
            'title': '',
            'min_delivery_days': None,
            'vat_rate': self.decimal('24.00'),
            'net': self.money('4.56'),
            'vat': self.money('1.44'),
            'weight_dimension_rate': 250.0
        })

    def test_get_address(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.get_address('billing'))

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'billing': 'BILLING'})
        self.assertEqual(adapter.get_address('billing'), 'BILLING')

    def fill_address(self, key):
        adapter = IShoppingSite(self.portal)
        session = adapter.getSessionData(create=True)
        names = ['city', 'last_name', 'first_name', 'email', 'phone', 'post', 'street']
        address = {}
        for name in names:
            address[name] = name.upper()
        session.set('collective.cart.core', {key: address})

    def test_is_address_filled(self):
        adapter = IShoppingSite(self.portal)
        self.assertFalse(adapter.is_address_filled('billing'))

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'billing': {}})
        self.assertFalse(adapter.is_address_filled('billing'))

        self.fill_address('billing')
        self.assertTrue(adapter.is_address_filled('billing'))

        billing = adapter.get_address('billing')
        del billing['email']
        adapter.update_cart('billing', billing)
        self.assertFalse(adapter.is_address_filled('billing'))

    def test_billing_same_as_shipping(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.billing_same_as_shipping)

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'billing_same_as_shipping': False})
        self.assertFalse(adapter.billing_same_as_shipping)

        adapter.update_cart('billing_same_as_shipping', True)
        self.assertTrue(adapter.billing_same_as_shipping)

    def test_is_addresses_filled(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.is_addresses_filled)

        self.fill_address('billing')
        self.assertFalse(adapter.is_addresses_filled)

        adapter.update_cart('billing_same_as_shipping', True)
        self.assertTrue(adapter.is_addresses_filled)

        adapter.update_cart('billing_same_as_shipping', False)
        self.assertFalse(adapter.is_addresses_filled)

        self.fill_address('shipping')
        adapter.update_cart('billing_same_as_shipping', True)

    def test_get_info(self):
        adapter = IShoppingSite(self.portal)
        self.assertEqual(adapter.get_info('NAME'), {
            'first_name': '',
            'last_name': '',
            'organization': '',
            'vat': '',
            'email': '',
            'street': '',
            'post': '',
            'city': '',
            'phone': '',
        })

        membership = getToolByName(self.portal, 'portal_membership')
        member = membership.getAuthenticatedMember()
        member.setProperties(fullname='First', email="fullname@email.com")
        self.assertEqual(adapter.get_info('billing'), {
            'first_name': 'First',
            'last_name': '',
            'organization': '',
            'vat': '',
            'email': 'fullname@email.com',
            'street': '',
            'post': '',
            'city': '',
            'phone': '',
        })

        member.setProperties(fullname='First Last', email="fullname@email.com")
        self.assertEqual(adapter.get_info('billing'), {
            'first_name': 'First',
            'last_name': 'Last',
            'organization': '',
            'vat': '',
            'email': 'fullname@email.com',
            'street': '',
            'post': '',
            'city': '',
            'phone': '',
        })

        member.setProperties(fullname='First Middle Last', email="fullname@email.com")
        self.assertEqual(adapter.get_info('billing'), {
            'first_name': 'First',
            'last_name': 'Middle Last',
            'organization': '',
            'vat': '',
            'email': 'fullname@email.com',
            'street': '',
            'post': '',
            'city': '',
            'phone': '',
        })

        self.fill_address('billing')
        self.assertEqual(adapter.get_info('billing'), {
            'city': 'CITY',
            'email': 'EMAIL',
            'first_name': 'FIRST_NAME',
            'last_name': 'LAST_NAME',
            'organization': '',
            'phone': 'PHONE',
            'post': 'POST',
            'street': 'STREET',
            'vat': '',
        })

    def create_cart_container(self):
        container = createContentInContainer(self.portal, 'collective.cart.core.CartContainer',
            id='cart-container', checkConstraints=False)
        modified(container)
        return container

    def test_create_cart(self):
        adapter = IShoppingSite(self.portal)
        adapter.create_cart()
        self.assertIsNone(adapter.get_cart('1'))

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.create_cart_container()
        adapter.create_cart()
        self.assertIsNone(adapter.get_cart('1'))

        items = {
            'id': '1',
            'title': 'Ärticle1',
            'description': 'Description of Ärticle1',
        }
        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': items}})
        adapter.create_cart()
        cart = adapter.get_cart('1')
        carticle = cart.get('1')
        self.assertEqual(carticle.title, items['title'])
        self.assertEqual(carticle.description, items['description'])

        adapter.update_cart('shipping_method', {'uuid': 'UUID', 'title': 'Shipping Methös 1'})
        adapter.create_cart()
        cart = adapter.get_cart('2')
        carticle = cart.get('1')
        self.assertEqual(carticle.title, items['title'])
        self.assertEqual(carticle.description, items['description'])
        shipping_method = cart.get('shipping_method')
        self.assertEqual(shipping_method.title, 'Shipping Methös 1')

        adapter.update_cart('billing', {'first_name': 'FIRST_NAME'})
        adapter.create_cart()
        cart = adapter.get_cart('3')
        carticle = cart.get('1')
        self.assertEqual(carticle.title, items['title'])
        self.assertEqual(carticle.description, items['description'])
        shipping_method = cart.get('shipping_method')
        self.assertEqual(shipping_method.title, 'Shipping Methös 1')
        billing = cart.get('billing')
        self.assertEqual(billing.first_name, 'FIRST_NAME')
        shipping = cart.get('shipping')
        self.assertIsNone(shipping)

        adapter.update_cart('shipping', {'first_name': 'FIRST_NAME'})
        adapter.create_cart()
        cart = adapter.get_cart('4')
        carticle = cart.get('1')
        self.assertEqual(carticle.title, items['title'])
        self.assertEqual(carticle.description, items['description'])
        shipping_method = cart.get('shipping_method')
        self.assertEqual(shipping_method.title, 'Shipping Methös 1')
        billing = cart.get('billing')
        self.assertEqual(billing.first_name, 'FIRST_NAME')
        shipping = cart.get('shipping')
        self.assertEqual(shipping.first_name, 'FIRST_NAME')

        adapter.update_cart('billing_same_as_shipping', True)
        adapter.create_cart()
        cart = adapter.get_cart('5')
        carticle = cart.get('1')
        self.assertEqual(carticle.title, items['title'])
        self.assertEqual(carticle.description, items['description'])
        shipping_method = cart.get('shipping_method')
        self.assertEqual(shipping_method.title, 'Shipping Methös 1')
        billing = cart.get('billing')
        self.assertEqual(billing.first_name, 'FIRST_NAME')
        shipping = cart.get('shipping')
        self.assertIsNone(shipping)

        adapter.create_cart('7')
        cart = adapter.get_cart('6')
        self.assertIsNone(cart)
        cart = adapter.get_cart('7')
        carticle = cart.get('1')
        self.assertEqual(carticle.title, items['title'])
        self.assertEqual(carticle.description, items['description'])
        shipping_method = cart.get('shipping_method')
        self.assertEqual(shipping_method.title, 'Shipping Methös 1')
        billing = cart.get('billing')
        self.assertEqual(billing.first_name, 'FIRST_NAME')
        shipping = cart.get('shipping')
        self.assertIsNone(shipping)

    def create_folder(self, parent=None, **kwargs):
        if parent is None:
            parent = self.portal
        folder = parent[parent.invokeFactory('Folder', **kwargs)]
        folder.reindexObject()
        return folder

    def create_doc(self, parent, **kwargs):
        doc = parent[parent.invokeFactory('Document', **kwargs)]
        doc.reindexObject()
        return doc

    def test_get_brain_for_text(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.get_brain_for_text('name'))

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertIsNone(adapter.get_brain_for_text('name'))

        folder = self.create_folder(id='name')
        self.assertIsNone(adapter.get_brain_for_text('name'))

        doc = self.create_doc(folder, id='doc')
        self.assertEqual(adapter.get_brain_for_text('name').getObject(), doc)

    def test_update_address(self):
        adapter = IShoppingSite(self.portal)
        data = {}
        self.assertEqual(adapter.update_address('address', data), u'First name is missing.')

        data = {'address_first_name': 'F|RST'}
        self.assertEqual(adapter.update_address('address', data), u'Last name is missing.')

        data = {'address_first_name': 'F|RST', 'address_last_name': 'LÄST'}
        self.assertEqual(adapter.update_address('address', data), u'Invalid e-mail address.')

        data = {'address_first_name': 'F|RST', 'address_last_name': 'LÄST', 'address_email': 'EMAIL'}
        self.assertEqual(adapter.update_address('address', data), u'Invalid e-mail address.')

        data = {'address_first_name': 'F|RST', 'address_last_name': 'LÄST', 'address_email': 'first.last@email.com'}
        self.assertEqual(adapter.update_address('address', data), u'Street address is missing.')

        data = {'address_first_name': 'F|RST', 'address_last_name': 'LÄST', 'address_email': 'first.last@email.com', 'address_street': 'STR€€T'}
        self.assertEqual(adapter.update_address('address', data), u'Post code is missing.')

        data = {'address_first_name': 'F|RST', 'address_last_name': 'LÄST', 'address_email': 'first.last@email.com', 'address_street': 'STR€€T',
            'address_post': 'PÖST'}
        self.assertEqual(adapter.update_address('address', data), u'City is missing.')

        data = {'address_first_name': 'F|RST', 'address_last_name': 'LÄST', 'address_email': 'first.last@email.com', 'address_street': 'STR€€T',
            'address_post': 'PÖST', 'address_city': 'C|TY'}
        self.assertEqual(adapter.update_address('address', data), u'Phone number is missing.')

        data = {'address_first_name': 'F|RST', 'address_last_name': 'LÄST', 'address_email': 'first.last@email.com', 'address_street': 'STR€€T',
            'address_city': 'C|TY', 'address_post': 'PÖST', 'address_phone': 'PHÖNE'}
        self.assertIsNone(adapter.update_address('address', data))

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {})
        self.assertIsNone(adapter.update_address('address', data))
        self.assertEqual(adapter.get_address('address'), {'first_name': 'F|RST', 'last_name': 'LÄST',
            'email': 'first.last@email.com', 'street': 'STR€€T', 'post': 'PÖST', 'city': 'C|TY', 'phone': 'PHÖNE'})

        data = {'address_first_name': 'FIRST', 'address_last_name': 'LAST', 'address_email': 'first.last@email.com', 'address_street': 'STR€€T',
            'address_post': 'PÖST', 'address_city': 'C|TY', 'address_phone': 'PHÖNE'}
        self.assertIsNone(adapter.update_address('address', data))
        self.assertEqual(adapter.get_address('address'), {'first_name': 'FIRST', 'last_name': 'LAST',
            'email': 'first.last@email.com', 'street': 'STR€€T', 'post': 'PÖST', 'city': 'C|TY', 'phone': 'PHÖNE'})
