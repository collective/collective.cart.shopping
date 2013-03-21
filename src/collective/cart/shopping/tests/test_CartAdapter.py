# -*- coding: utf-8 -*-
from collective.cart.core.interfaces import ICartAdapter as IBaseCartAdapter
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent import modified


class CartAdapterTestCase(IntegrationTestCase):
    """TestCase for CartAdapter"""

    def test_subclass(self):
        from collective.cart.core.adapter.cart import CartAdapter as BaseCartAdapter
        from collective.cart.shopping.adapter.cart import CartAdapter
        self.assertTrue(issubclass(CartAdapter, BaseCartAdapter))
        self.assertTrue(issubclass(ICartAdapter, IBaseCartAdapter))

    def test_context(self):
        from collective.cart.shopping.adapter.cart import CartAdapter
        from collective.cart.shopping.interfaces import ICart
        self.assertEqual(getattr(CartAdapter, 'grokcore.component.directive.context'), ICart)

    def test_provides(self):
        from collective.cart.shopping.adapter.cart import CartAdapter
        self.assertEqual(getattr(CartAdapter, 'grokcore.component.directive.provides'), ICartAdapter)

    def create_cart(self, shop=None):
        """Create cart."""
        if shop is None:
            # Create shop.
            shop = createContentInContainer(self.portal, 'collective.cart.shopping.Shop', id='shop',
                checkConstraints=False, title='Shop')
            modified(shop)
        # Cart container is created with event subscriber.
        cart_container = shop['cart-container']
        # Create cart.
        cart = createContentInContainer(cart_container, 'collective.cart.core.Cart', id='1',
            checkConstraints=False)
        modified(cart)
        return cart

    def create_cart_article(self, cart, uuid=None, gross=None):
        title = 'Ärticle{}'.format(uuid)
        description = 'Descriptiön of Ärticle{}'.format(uuid)
        sku = u'SKÖ{}'.format(uuid)
        if gross is None:
            gross = self.money('12.40')
        carticle = createContentInContainer(cart, 'collective.cart.core.CartArticle', id=uuid,
            checkConstraints=False, title=title, description=description, gross=gross,
            quantity=2, sku=sku, vat_rate=Decimal('24.00'))
        modified(carticle)
        return carticle

    def create_article(self, context=None):
        if context is None:
            context = self.portal
        article = createContentInContainer(self.portal, 'collective.cart.core.Article', id='article', checkConstraints=False,
            money=self.money('12.40'), vat=Decimal('24.00'))
        modified(article)
        return article

    def test_instance(self):
        from collective.cart.shopping.adapter.cart import CartAdapter
        cart = self.create_cart()
        self.assertIsInstance(ICartAdapter(cart), CartAdapter)

    def test_articles(self):
        cart = self.create_cart()
        self.assertEqual(len(ICartAdapter(cart).articles), 0)

        article = self.create_article()
        uuid = IUUID(article)
        carticle = self.create_cart_article(cart, uuid)

        description = u'Descriptiön of Ärticle{}'.format(uuid)
        title = u'Ärticle{}'.format(uuid)
        sku = u'SKÖ{}'.format(uuid)
        self.assertEqual(ICartAdapter(cart).articles, [{
            'description': description,
            'gross': self.money('12.40'),
            'gross_subtotal': self.money('24.80'),
            'locale_gross_subtotal': u'24.80 €',
            'image_url': 'http://nohost/plone/fallback.png',
            'obj': carticle,
            'quantity': 2,
            'sku': sku,
            'title': title,
            'url': 'http://nohost/plone/article',
            'vat_rate': Decimal('24.00')
        }])

        self.portal.manage_delObjects(['article'])
        self.assertEqual(ICartAdapter(cart).articles, [{
            'description': description,
            'gross': self.money('12.40'),
            'gross_subtotal': self.money('24.80'),
            'image_url': None,
            'locale_gross_subtotal': u'24.80 €',
            'obj': carticle,
            'quantity': 2,
            'sku': sku,
            'title': title,
            'url': None,
            'vat_rate': Decimal('24.00')
        }])

    def test_articles_total(self):
        cart = self.create_cart()
        adapter = ICartAdapter(cart)
        self.assertEqual(adapter.articles_total, self.money('0.00'))

        self.create_cart_article(cart, '1')
        self.create_cart_article(cart, '2', gross=self.money('10.00'))
        self.assertEqual(adapter.articles_total, self.money('44.80'))

    def test_total(self):
        cart = self.create_cart()
        adapter = ICartAdapter(cart)
        self.assertEqual(adapter.total, self.money('0.00'))

        self.create_cart_article(cart, '1')
        self.create_cart_article(cart, '2', gross=self.money('10.00'))
        self.assertEqual(adapter.total, self.money('44.80'))

        self.create_content('collective.cart.shipping.CartShippingMethod', cart, id='cart-shipping-method', vat_rate=Decimal('24.00'), gross=self.money('24.80'), net=self.money('20.00'),
            vat=self.money('4.80'))
        self.assertEqual(adapter.total, self.money('69.60'))

    def test_shipping_method(self):
        cart = self.create_cart()
        adapter = ICartAdapter(cart)
        shipping_method = self.create_content('collective.cart.shipping.CartShippingMethod', cart, id='cart-shipping-method', vat_rate=Decimal('24.00'))
        self.assertEqual(adapter.shipping_method.getObject(), shipping_method)

    def test_locale_shipping_method(self):
        cart = self.create_cart()
        adapter = ICartAdapter(cart)
        self.create_content('collective.cart.shipping.CartShippingMethod', cart, id='cart-shipping-method', vat_rate=Decimal('24.00'), gross=self.money('24.80'))
        self.assertEqual(adapter.locale_shipping_method(), {
            'gross': u'24.80 €',
            'is_free': False,
            'title': '',
            'vat_rate': self.decimal('24.00'),
        })

    def create_articles(self, cart):
        article1 = createContentInContainer(cart, 'collective.cart.core.CartArticle',
            id='article1', weight=100.0, quantity=1, gross=Money(10.0, currency=u'EUR'), orig_uuid='UUID')
        modified(article1)
        article2 = createContentInContainer(cart, 'collective.cart.core.CartArticle',
            id='article2', weight=200.0, quantity=2, gross=Money(20.0, currency=u'EUR'), orig_uuid='UUID')
        modified(article2)
        return (article1, article2)

    def test__calculated_weight(self):
        cart = self.create_cart()
        self.create_articles(cart)
        self.assertEqual(ICartAdapter(cart)._calculated_weight(), 0.5)

    def test_shipping_gross_money(self):
        cart = self.create_cart()
        adapter = ICartAdapter(cart)
        gross = self.money('24.80')
        vat = self.money('4.80')
        net = self.money('20.00')
        self.create_content('collective.cart.shipping.CartShippingMethod', cart, id='cart-shipping-method', vat_rate=Decimal('24.00'), gross=gross, net=net, vat=vat)
        self.assertEqual(adapter.shipping_gross_money, gross)

    def test_shipping_net_money(self):
        cart = self.create_cart()
        adapter = ICartAdapter(cart)
        self.assertEqual(adapter.shipping_net_money, self.money('0.00'))

        gross = self.money('24.80')
        vat = self.money('4.80')
        net = self.money('20.00')
        self.create_content('collective.cart.shipping.CartShippingMethod', cart, id='cart-shipping-method', vat_rate=Decimal('24.00'), gross=gross, net=net, vat=vat)
        self.assertEqual(adapter.shipping_net_money, net)

    def test_shipping_vat_money(self):
        cart = self.create_cart()
        adapter = ICartAdapter(cart)
        self.assertEqual(adapter.shipping_vat_money, self.money('0.00'))

        gross = self.money('24.80')
        vat = self.money('4.80')
        net = self.money('20.00')
        self.create_content('collective.cart.shipping.CartShippingMethod', cart, id='cart-shipping-method', vat_rate=Decimal('24.00'), gross=gross, net=net, vat=vat)
        self.assertEqual(adapter.shipping_vat_money, vat)

    def create_customer_info(self, cart, name):
        info = createContentInContainer(cart, 'collective.cart.shopping.CustomerInfo',
            checkConstraints=False, id=name)
        modified(info)
        return info

    def test_get_address(self):
        cart = self.create_cart()
        adapter = ICartAdapter(cart)
        self.assertIsNone(adapter.get_address('something'))
        self.assertIsNone(adapter.get_address('billing'))
        self.assertIsNone(adapter.get_address('shipping'))

        something = self.create_customer_info(cart, 'something')
        self.assertEqual(adapter.get_address('something').getObject(), something)
        self.assertIsNone(adapter.get_address('billing'))
        self.assertIsNone(adapter.get_address('shipping'))

        billing = self.create_customer_info(cart, 'billing')
        self.assertEqual(adapter.get_address('something').getObject(), something)
        self.assertEqual(adapter.get_address('billing').getObject(), billing)
        self.assertEqual(adapter.get_address('shipping').getObject(), billing)

        cart.billing_same_as_shipping = False
        self.assertEqual(adapter.get_address('something').getObject(), something)
        self.assertEqual(adapter.get_address('billing').getObject(), billing)
        self.assertIsNone(adapter.get_address('shipping'))

        shipping = self.create_customer_info(cart, 'shipping')
        self.assertEqual(adapter.get_address('something').getObject(), something)
        self.assertEqual(adapter.get_address('billing').getObject(), billing)
        self.assertEqual(adapter.get_address('shipping').getObject(), shipping)
