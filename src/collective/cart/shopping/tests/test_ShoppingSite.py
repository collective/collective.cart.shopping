# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.adapter.interface import ShoppingSite
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.interface import alsoProvides

import mock


class ShoppingSiteTestCase(IntegrationTestCase):
    """TestCase for ShoppingSite"""

    def test_subclass(self):
        from collective.cart.core.adapter.interface import ShoppingSite as BaseShoppingSite
        self.assertTrue(issubclass(ShoppingSite, BaseShoppingSite))
        from collective.cart.core.interfaces import IShoppingSite as IBaseShoppingSite
        self.assertTrue(issubclass(IShoppingSite, IBaseShoppingSite))

    def test_instance(self):
        self.assertIsInstance(IShoppingSite(self.portal), ShoppingSite)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(IShoppingSite, IShoppingSite(self.portal)))

    def test_locales(self):
        adapter = IShoppingSite(self.portal)
        self.assertEqual(adapter.locale(), 'default')

    def test_format_money(self):
        adapter = IShoppingSite(self.portal)
        money = self.money('12.40')
        self.assertEqual(adapter.format_money(money), u'12.40 €')

    @mock.patch('collective.cart.core.adapter.interface.ShoppingSite.cart_article_listing')
    def test_cart_article_listing(self, cart_article_listing):
        cart_article_listing.return_value = [{'vat_rate': 24.0}, {'vat_rate': 10.0}]
        adapter = IShoppingSite(self.portal)
        self.assertEqual(adapter.cart_article_listing(), [{'vat_rate': u'24%'}, {'vat_rate': u'10%'}])

    @mock.patch('collective.cart.shopping.adapter.interface.IStock')
    @mock.patch('collective.cart.shopping.adapter.interface.BaseShoppingSite.clean_articles_in_cart')
    def test_clean_articles_in_cart(self, clean_articles_in_cart, IStock):
        article1 = self.create_content('collective.cart.core.Article')
        uuid1 = IUUID(article1)
        article2 = self.create_content('collective.cart.core.Article')
        uuid2 = IUUID(article2)
        clean_articles_in_cart.return_value = {uuid1: {}, uuid2: {}}
        IStock().stock = 0
        instance = IShoppingSite(self.portal)
        instance.update_cart = mock.Mock()
        self.assertEqual(instance.clean_articles_in_cart(), {})
        instance.update_cart.assert_called_with('articles', {})

    def test_articles_total(self):
        adapter = IShoppingSite(self.portal)
        adapter.cart_article_listing = mock.MagicMock()
        self.assertEqual(adapter.articles_total(), self.money('0.00'))

        adapter.cart_article_listing.return_value = [
            {'gross': self.money('10.00'), 'quantity': 2}, {'gross': self.money('5.00'), 'quantity': 4}]
        self.assertEqual(adapter.articles_total(), self.money('40.00'))

    def test_locale_articles_total(self):
        adapter = IShoppingSite(self.portal)
        articles_total = mock.Mock()
        adapter.articles_total = articles_total
        adapter.articles_total = mock.Mock(return_value=self.money('40.00'))
        self.assertEqual(adapter.locale_articles_total(), u'40.00 €')

    def test_shipping_methods(self):
        adapter = IShoppingSite(self.portal)
        self.assertEqual(len(adapter.shipping_methods()), 0)

        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_content('collective.cart.shipping.ShippingMethodContainer')
        self.create_atcontent('ShippingMethod', container, id='shippingmethod1')
        self.assertEqual(len(adapter.shipping_methods()), 1)

    def test_shipping_method(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_method())

        adapter.cart = mock.MagicMock(return_value={'shipping_method': 'SHIPPINIG_METHOD'})
        self.assertEqual(adapter.shipping_method(), 'SHIPPINIG_METHOD')

    def test__calculated_weight(self):
        adapter = IShoppingSite(self.portal)
        self.assertEqual(adapter._calculated_weight(), 0.0)

        adapter.shipping_method = mock.Mock()
        self.assertEqual(adapter._calculated_weight(), 0.0)
        self.assertEqual(adapter._calculated_weight('RATE'), 0.0)
        self.assertEqual(adapter._calculated_weight(10.0), 0.0)

        adapter.cart_article_listing = mock.MagicMock(return_value=[{'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1}])
        self.assertEqual(adapter._calculated_weight(10.0), 0.1)

        adapter.cart_article_listing = mock.MagicMock(return_value=[
            {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1},
            {'weight': 10.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 1}])
        self.assertEqual(adapter._calculated_weight(10.0), 0.16)

        adapter.cart_article_listing = mock.MagicMock(return_value=[
            {'weight': 100.0, 'depth': 10.0, 'height': 20.0, 'width': 30.0, 'quantity': 2, 'vat_rate': 24.0}])
        self.assertEqual(adapter._calculated_weight(10.0), 0.2)

    def test_get_shipping_gross_money(self):
        alsoProvides(self.portal, IShoppingSiteRoot)
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.get_shipping_gross_money('UUID'))

        container = self.create_content('collective.cart.shipping.ShippingMethodContainer')
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1')
        uuid1 = IUUID(shippingmethod1)
        self.assertEqual(adapter.get_shipping_gross_money(uuid1), self.money('0.00'))

    def test_shipping_gross_money(self):
        adapter = IShoppingSite(self.portal)
        adapter.shipping_method = mock.Mock(return_value=None)
        self.assertIsNone(adapter.shipping_gross_money())

        adapter.get_shipping_gross_money = mock.Mock()
        adapter.shipping_method = mock.Mock(return_value={'uuid': 'UUID'})
        adapter.shipping_gross_money()
        adapter.get_shipping_gross_money.assert_called_with('UUID')

    def test_locale_shipping_gross(self):
        adapter = IShoppingSite(self.portal)
        adapter.shipping_gross_money = mock.Mock(return_value=self.money('10.00'))
        self.assertEqual(adapter.locale_shipping_gross(), u'10.00 €')

    def test_shipping_vat_money(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_vat_money())

        adapter.shipping_gross_money = mock.Mock(return_value=self.money('10.00'))
        adapter.shipping_method = mock.Mock(return_value={'vat_rate': 24.0})
        self.assertEqual(adapter.shipping_vat_money(), self.money('2.40'))

    def test_shipping_net_money(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_net_money())

        adapter.shipping_gross_money = mock.Mock(return_value=self.money('10.00'))
        adapter.shipping_vat_money = mock.Mock(return_value=self.money('2.40'))
        self.assertEqual(adapter.shipping_net_money(), self.money('7.60'))

    def test_total(self):
        adapter = IShoppingSite(self.portal)
        adapter.articles_total = mock.Mock(return_value=self.money('2.00'))
        self.assertEqual(adapter.total(), self.money('2.00'))

        adapter.shipping_gross_money = mock.Mock(return_value=self.money('10.00'))
        self.assertEqual(adapter.total(), self.money('12.00'))

    def test_locale_total(self):
        adapter = IShoppingSite(self.portal)
        adapter.total = mock.Mock(return_value=self.money('10.00'))
        self.assertEqual(adapter.locale_total(), u'10.00 €')

    def test_update_shipping_method(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.shipping_method())

        adapter.update_shipping_method()
        self.assertIsNone(adapter.shipping_method())

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {
            '1': {'gross': self.money('10.00'), 'quantity': 2, 'vat_rate': 24.0}
        }})
        adapter.update_shipping_method()
        self.assertIsNone(adapter.shipping_method())

        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_content('collective.cart.shipping.ShippingMethodContainer')
        shippingmethod1 = self.create_atcontent('ShippingMethod', container, id='shippingmethod1', vat=self.decimal('24.00'))
        uuid1 = IUUID(shippingmethod1)
        adapter.update_shipping_method()
        self.assertEqual(adapter.shipping_method(), {
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

        self.assertEqual(adapter.shipping_method(), {
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
        self.assertEqual(adapter.shipping_method(), {
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
        self.assertEqual(adapter.shipping_method(), {
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
        self.assertEqual(adapter.shipping_method(), {
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
        self.assertEqual(adapter.shipping_method(), {
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
        self.assertEqual(adapter.shipping_method(), {
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
        self.assertIsNone(adapter.shipping_method())
        adapter.update_shipping_method(uuid1)
        self.assertEqual(adapter.shipping_method(), {
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

        adapter.cart = mock.Mock(return_value={'billing': 'BILLING'})
        self.assertEqual(adapter.get_address('billing'), 'BILLING')

    def test_is_address_filled(self):
        adapter = IShoppingSite(self.portal)
        self.assertFalse(adapter.is_address_filled('billing'))

        adapter.get_address = mock.Mock(return_value={})
        self.assertFalse(adapter.is_address_filled('billing'))

        names = ['city', 'last_name', 'first_name', 'email', 'phone', 'post', 'street']
        address = {}
        for name in names:
            address[name] = name.upper()

        adapter.get_address = mock.Mock(return_value=address)
        self.assertTrue(adapter.is_address_filled('billing'))

        del address['email']
        self.assertFalse(adapter.is_address_filled('billing'))

    def test_billing_same_as_shipping(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.billing_same_as_shipping())

        adapter.cart = mock.Mock(return_value={'billing_same_as_shipping': False})
        self.assertFalse(adapter.billing_same_as_shipping())

        adapter.cart = mock.Mock(return_value={'billing_same_as_shipping': True})
        self.assertTrue(adapter.billing_same_as_shipping())

    def test_is_addresses_filled(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.is_addresses_filled())

        adapter.is_address_filled = mock.Mock(return_value=True)
        self.assertTrue(adapter.is_addresses_filled())
        self.assertEqual(adapter.is_address_filled.call_args_list, [(('billing',),), (('shipping',),)])

        adapter.billing_same_as_shipping = mock.Mock(return_value=True)
        self.assertTrue(adapter.is_addresses_filled())
        self.assertEqual(adapter.is_address_filled.call_args_list, [(('billing',),), (('shipping',),), (('billing',),)])

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

        names = ['city', 'last_name', 'first_name', 'email', 'phone', 'post', 'street']
        address = {}
        for name in names:
            address[name] = name.upper()
        adapter.get_address = mock.Mock(return_value=address)

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

    @mock.patch('collective.cart.core.adapter.interface.ShoppingSite.create_order')
    def test_create_cart(self, create_order):
        adapter = IShoppingSite(self.portal)

        create_order.return_value = None
        self.assertIsNone(adapter.create_order())

        order1 = self.create_content('collective.cart.core.Order', id='1')
        create_order.return_value = order1
        self.assertEqual(adapter.create_order(), order1)
        with self.assertRaises(KeyError):
            order1['shipping_method']
        with self.assertRaises(KeyError):
            order1['billing']
        with self.assertRaises(KeyError):
            order1['shipping']

        adapter.shipping_method = mock.Mock(return_value={'gross': self.money('10.00')})
        order2 = self.create_content('collective.cart.core.Order', id='2')
        create_order.return_value = order2
        self.assertEqual(adapter.create_order(), order2)
        self.assertIsNotNone(order2['shipping_method'])
        with self.assertRaises(KeyError):
            order2['billing']
        with self.assertRaises(KeyError):
            order2['shipping']

        names = ['city', 'last_name', 'first_name', 'email', 'phone', 'post', 'street']
        address = {}
        for name in names:
            address[name] = name.upper()
        adapter.get_address = mock.Mock(return_value=address)
        adapter.billing_same_as_shipping = mock.Mock(return_value=True)
        order3 = self.create_content('collective.cart.core.Order', id='3')
        create_order.return_value = order3
        self.assertEqual(adapter.create_order(), order3)
        self.assertIsNotNone(order3['shipping_method'])
        self.assertIsNotNone(order3['billing'])
        with self.assertRaises(KeyError):
            order3['shipping']

        adapter.billing_same_as_shipping = mock.Mock(return_value=False)
        order4 = self.create_content('collective.cart.core.Order', id='4')
        create_order.return_value = order4
        self.assertEqual(adapter.create_order(), order4)
        self.assertIsNotNone(order4['shipping_method'])
        self.assertIsNotNone(order4['billing'])
        self.assertIsNotNone(order4['shipping'])

    def test_get_brain_for_text(self):
        alsoProvides(self.portal, IShoppingSiteRoot)
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.get_brain_for_text('name'))

        folder = self.create_atcontent('Folder', id='name')
        self.assertIsNone(adapter.get_brain_for_text('name'))

        doc = self.create_atcontent('Document', folder, id='doc')
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

        adapter.get_address = mock.Mock(return_value=None)
        adapter.update_cart = mock.Mock()
        self.assertIsNone(adapter.update_address('address', data))
        adapter.update_cart.assert_called_with('address', {
            'city': 'C|TY',
            'email': 'first.last@email.com',
            'first_name': 'F|RST',
            'last_name': 'LÄST',
            'phone': 'PHÖNE',
            'post': 'PÖST',
            'street': 'STR€€T',
        })

        names = ['city', 'last_name', 'first_name', 'email', 'phone', 'post', 'street']
        address = {}
        for name in names:
            address[name] = name.upper()
        adapter.get_address = mock.Mock(return_value=address)
        self.assertIsNone(adapter.update_address('address', data))
        adapter.update_cart.assert_called_with('address', {
            'city': 'C|TY',
            'email': 'first.last@email.com',
            'first_name': 'F|RST',
            'last_name': 'LÄST',
            'phone': 'PHÖNE',
            'post': 'PÖST',
            'street': 'STR€€T',
        })

    @mock.patch('collective.cart.shopping.adapter.interface.IStock')
    def test_reduce_stocks(self, IStock):
        adapter = IShoppingSite(self.portal)
        article1 = self.create_content('collective.cart.core.Article')
        uuid1 = IUUID(article1)
        article2 = self.create_content('collective.cart.core.Article')
        uuid2 = IUUID(article2)
        adapter.cart_article_listing = mock.Mock(return_value=[{'id': uuid1, 'quantity': 1}, {'id': uuid2, 'quantity': 2}])
        adapter.reduce_stocks()
        self.assertEqual(IStock().sub_stock.call_args_list, [((1,),), ((2,),)])

    def test_link_to_order(self):
        adapter = IShoppingSite(self.portal)
        adapter.get_order = mock.Mock()
        adapter.link_to_order('ORDER_ID')
        adapter.get_order.assert_called_with('ORDER_ID')
        self.assertTrue(adapter.get_order().absolute_url.called)
