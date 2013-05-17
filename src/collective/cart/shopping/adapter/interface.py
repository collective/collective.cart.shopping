from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ATContentTypes.interfaces import IATDocument
from Products.ATContentTypes.interfaces import IATFolder
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation import validation
from collective.behavior.price.interfaces import ICurrency
from collective.behavior.size.interfaces import ISize
from collective.behavior.stock.interfaces import IStock
from collective.behavior.vat.interfaces import IAdapter as IVATAdapter
from collective.cart.core.adapter.interface import ShoppingSite as BaseShoppingSite
from collective.cart.shipping.interfaces import IShippingMethod
from collective.cart.shopping import _
from collective.cart.shopping.event import ArticleAddedToCartEvent
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import ICartArticleMultiAdapter
from collective.cart.shopping.interfaces import ILocaleUtility
from collective.cart.shopping.interfaces import IPriceUtility
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IShoppingSiteMultiAdapter
from collective.cart.shopping.schema import CustomerInfoSchema
from decimal import Decimal
from moneyed import Money
from moneyed.localization import DEFAULT
from moneyed.localization import format_money
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import adapts
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface
from zope.interface import implements
from zope.lifecycleevent import modified
from zope.publisher.interfaces.browser import IBrowserRequest

import types


class ShoppingSite(BaseShoppingSite):
    """Adapter for shopping site"""
    implements(IShoppingSite)

    def locale(self):
        """Returns locale for localizing money

        :rtype: str
        """
        code = self.context.restrictedTraverse('@@plone_portal_state').locale().getLocaleID()
        return getUtility(ILocaleUtility)(code) or DEFAULT

    def format_money(self, money):
        """Returns locale formated money

        :param money: Money
        :type money: moneyed.Money

        :rtype: unicode
        """
        return format_money(money, locale=self.locale())

    def cart_article_listing(self):
        """Returns list of cart articles in session for view

        :rtype: list
        """
        res = []
        adapter = IVATAdapter(self.context)
        for article in super(ShoppingSite, self).cart_article_listing():
            article = article.copy()
            article['vat_rate'] = adapter.percent(article['vat_rate'])
            res.append(article)
        return res

    def clean_articles_in_cart(self):
        """Clean articles in cart like:

        Remove article from cart if article no longer exist in shop or the stock is zero.

        :rtype: list
        """
        cart_articles = super(ShoppingSite, self).clean_articles_in_cart()
        if cart_articles:
            articles = cart_articles.copy()
            number_of_articles = len(articles)
            for key in cart_articles:
                obj = self.get_object(UID=key)
                if IStock(obj).stock == 0:
                    del articles[key]

            if len(articles) != number_of_articles:
                self.update_cart('articles', articles)

            return articles

    def articles_total(self):
        """Returns total money of articles in cart

        :rtype: moneyed.Money
        """
        registry = getUtility(IRegistry)
        currency = registry.forInterface(ICurrency).default_currency
        res = Money(0.00, currency=currency)
        for item in self.cart_article_listing():
            res += item['gross'] * item['quantity']
        return res

    def locale_articles_total(self):
        """Returns localized total money amount and currency of articles in cart

        :rtype: str
        """
        return self.format_money(self.articles_total())

    def shipping_methods(self):
        """Returns list of shipping methods

        :rtype: list
        """
        methods = []
        if self.shop():
            methods = self.get_brains(IShippingMethod, path=self.shop_path(), sort_on='getObjPositionInParent')
        return methods

    def shipping_method(self):
        """Returns shipping method in cart"""
        if self.cart():
            return self.cart().get('shipping_method')

    def _calculated_weight(self, rate=None):
        weight = 0.0

        if self.shipping_method() and rate and isinstance(rate, float) and rate > 0.0:

            for article in self.cart_article_listing():
                weight_in_kg = article['weight'] / 1000.0
                dimension_weight = (article['depth'] * article['height'] * article['width'] / 10.0 ** 6) * rate
                if dimension_weight > weight_in_kg:
                    article_weight = dimension_weight
                else:
                    article_weight = weight_in_kg

                weight += article_weight * article['quantity']

        return weight

    def get_shipping_gross_money(self, uuid):
        """Get shipping gross money by uuid.

        :rtype: moneyed.Money
        """
        shipping_methods = self.shipping_methods()
        if shipping_methods:
            shipping_methods = [sm for sm in shipping_methods if sm.UID == uuid]
            if shipping_methods:
                shipping_method = shipping_methods[0]
                obj = shipping_method.getObject()
                rate = shipping_method.weight_dimension_rate
                shipping_fee = price = obj.shipping_fee()
                if isinstance(shipping_fee, types.FunctionType):
                    price = shipping_fee(self._calculated_weight(rate=rate))
                price = getUtility(IPriceUtility, name="string")(price)
                registry = getUtility(IRegistry)
                currency = registry.forInterface(ICurrency).default_currency
                return Money(price, currency=currency)

    def shipping_gross_money(self):
        """Returns shipping gross money

        :rtype: moneyed.Money
        """
        shipping_method = self.shipping_method()
        if shipping_method:
            return self.get_shipping_gross_money(shipping_method['uuid'])

    def locale_shipping_gross(self):
        """Returns localized money amount and currency for shipping gross cost

        :rtype: unicode
        """
        return self.format_money(self.shipping_gross_money())

    def shipping_vat_money(self):
        """Returns shipping vat money

        :rtype: moneyed.Money
        """
        shipping_gross_money = self.shipping_gross_money()
        if shipping_gross_money:
            currency = shipping_gross_money.currency
            money = Decimal(self.shipping_method()['vat_rate']) / 100 * shipping_gross_money
            price = getUtility(IPriceUtility, name="string")(money.amount)
            return Money(Decimal(price), currency)

    def shipping_net_money(self):
        """Returns shipping net money

        :rtype: moneyed.Money
        """
        shipping_gross_money = self.shipping_gross_money()
        if shipping_gross_money:
            return shipping_gross_money - self.shipping_vat_money()

    def total(self):
        """Returns total money in cart

        :rtype: moneyed.Money
        """
        total = self.articles_total()
        shipping_gross_money = self.shipping_gross_money()
        if shipping_gross_money:
            total += shipping_gross_money
        return total

    def locale_total(self):
        """Returns localized total amount and currency

        :rtype: unicode
        """
        return self.format_money(self.total())

    def update_shipping_method(self, uuid=None):
        if self.cart_articles():
            if self.shipping_methods():
                if uuid is None:
                    if not self.shipping_method():
                        shipping_method = self.shipping_methods()[0]
                        items = {
                            'title': shipping_method.Title,
                            'uuid': shipping_method.UID,
                            'min_delivery_days': shipping_method.min_delivery_days,
                            'max_delivery_days': shipping_method.max_delivery_days,
                            'vat_rate': shipping_method.vat,
                            'weight_dimension_rate': shipping_method.weight_dimension_rate,
                        }
                    else:
                        items = self.shipping_method()

                else:
                    smethods = [smethod for smethod in self.shipping_methods() if smethod.UID == uuid]
                    if smethods:
                        shipping_method = smethods[0]
                        items = {
                            'title': shipping_method.Title,
                            'uuid': shipping_method.UID,
                            'min_delivery_days': shipping_method.min_delivery_days,
                            'max_delivery_days': shipping_method.max_delivery_days,
                            'vat_rate': shipping_method.vat,
                            'weight_dimension_rate': shipping_method.weight_dimension_rate,
                        }
                        self.update_cart('shipping_method', items)

                    items = self.shipping_method()

                items['gross'] = self.shipping_gross_money()
                items['net'] = self.shipping_net_money()
                items['vat'] = self.shipping_vat_money()

                self.update_cart('shipping_method', items)

            else:
                self.remove_from_cart('shipping_method')

    def get_address(self, name):
        """Returns address by name

        :param name: 'billing' or 'shipping'
        :type name: str

        :rtype: dict
        """
        cart = self.cart()
        if cart:
            return cart.get(name)

    def is_address_filled(self, name):
        """Returns True if the address of name is filled else False

        :rtype: bool
        """
        info = self.get_address(name)
        if info:
            keyss = [keys for keys in CustomerInfoSchema.names() if CustomerInfoSchema.get(keys).required]
            for keys in keyss:
                if info.get(keys) is None:
                    return False
            return True
        else:
            return False

    def billing_same_as_shipping(self):
        """Returns True if billing cart is same as shipping

        :rtype: bool
        """
        cart = self.cart()
        if cart:
            return cart.get('billing_same_as_shipping')

    def is_addresses_filled(self):
        """Returns True if addresses in cart are filled else False

        :rtype: bool
        """
        if self.is_address_filled('billing'):
            return self.billing_same_as_shipping() or self.is_address_filled('shipping')

    def get_info(self, name):
        """Returns dictionary of address info by name

        :param name: 'billing' or 'shipping'
        :param type: str

        :rtype: dict
        """
        info = self.get_address(name)
        if info:
            return {
                'first_name': info['first_name'],
                'last_name': info['last_name'],
                'organization': info.get('organization', ''),
                'vat': info.get('vat', ''),
                'email': info['email'],
                'street': info['street'],
                'post': info.get('post', ''),
                'city': info['city'],
                'phone': info['phone'],
            }
        else:
            data = {
                'first_name': '',
                'last_name': '',
                'organization': '',
                'vat': '',
                'email': '',
                'street': '',
                'post': '',
                'city': '',
                'phone': '',
            }
            membership = getToolByName(self.context, 'portal_membership')
            if not membership.isAnonymousUser():
                member = membership.getAuthenticatedMember()
                fullname = member.getProperty('fullname')
                names = fullname.split(' ')
                data['first_name'] = names.pop(0)
                data['last_name'] = ' '.join(names)
                data['email'] = member.getProperty('email')

            return data

    def create_order(self, order_id=None):
        """Create order into order container from cart

        :rtype: collective.cart.core.Order
        """
        order = super(ShoppingSite, self).create_order(order_id=order_id)
        if order is not None:
            if self.shipping_method():
                shipping_method = createContentInContainer(order, 'collective.cart.shipping.OrderShippingMethod',
                        checkConstraints=False, id="shipping_method", **self.shipping_method())
                modified(shipping_method)
            order.billing_same_as_shipping = self.billing_same_as_shipping()
            if self.get_address('billing'):
                billing = createContentInContainer(order, 'collective.cart.shopping.CustomerInfo',
                        checkConstraints=False, id="billing", **self.get_address('billing'))
                modified(billing)
            if not order.billing_same_as_shipping and self.get_address('shipping'):
                shipping = createContentInContainer(order, 'collective.cart.shopping.CustomerInfo',
                        checkConstraints=False, id="shipping", **self.get_address('shipping'))
                modified(shipping)

        return order

    def get_brain_for_text(self, name):
        """Returns brain for displaying texts based on context name

        :param name: ID of context
        :type name: str

        :rtype: brain or None
        """
        brain = self.get_brain(IATFolder, path=self.shop_path(), depth=1, id=name)
        if brain:
            return self.get_brain(IATDocument, path=brain.getPath(), depth=1)

    def update_address(self, name, data):
        """Update address of cart and return message if there are one

        :param name: Name of address, such as billing and shipping.
        :type name: str

        :param data: Form data.
        :type data: dict

        :rtype: unicode or None
        """
        message = None

        items = data
        data = {}
        for key in items:
            text = '{}_'.format(name)
            if key.startswith(text):
                data[key[len(text):]] = items.get(key)

        if not data.get('first_name'):
            message = _(u'First name is missing.')

        elif not data.get('last_name'):
            message = _(u'Last name is missing.')

        elif not data.get('email') or validation.validatorFor('isEmail')(data.get('email')) != 1:
            message = _(u'Invalid e-mail address.')

        elif not data.get('street'):
            message = _(u'Street address is missing.')

        elif not data.get('post'):
            message = _(u'Post code is missing.')

        elif not data.get('city'):
            message = _(u'City is missing.')

        elif not data.get('phone'):
            message = _(u'Phone number is missing.')

        else:
            address = self.get_address(name)
            if address is not None:
                for key in data:
                    value = data.get(key)
                    if address.get(key) != value:
                        address[key] = value
            else:
                address = data
            self.update_cart(name, address)

        return message

    def reduce_stocks(self):
        """Reduce stocks from articles"""
        for item in self.cart_article_listing():
            uuid = item['id']
            quantity = item['quantity']
            obj = self.get_object(UID=uuid)
            IStock(obj).sub_stock(quantity)
            modified(obj)

    def link_to_order(self, order_id):
        """Returns link to order

        :param order_id: Order ID
        :type order_id: str

        :rtype: str
        """
        return self.get_order(order_id).absolute_url()


class ShoppingSiteMultiAdapter(object):
    """Multi adapter for shopping site"""

    adapts(Interface, IBrowserRequest)
    implements(IShoppingSiteMultiAdapter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def add_to_cart(self):
        """Add article to cart"""
        shopping_site = IShoppingSite(self.context)
        form = self.request.form
        add_to_cart = form.pop('form.buttons.AddToCart', None)
        subarticle = form.pop('subarticle', None)

        uuid = None
        quantity = '1'

        if subarticle is not None:

            uuids = subarticle
            parent_uuid = add_to_cart

            if not isinstance(uuids, list):
                uuids = [subarticle]

            for subarticle_uuid in uuids:
                parent = aq_parent(aq_inner(shopping_site.get_object(UID=subarticle_uuid)))
                if parent_uuid == IUUID(parent):
                    uuid = subarticle_uuid

                quantity = form.get(parent_uuid)

        uuid = uuid or add_to_cart

        if uuid is not None:

            quantity = form.get('quantity') or form.get(uuid) or quantity
            validate = validation.validatorFor('isInt')
            url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()
            message = None

            if quantity is not None and validate(quantity) == 1:
                quantity = int(quantity)
                obj = shopping_site.get_object(UID=uuid)
                if obj:
                    item = IArticleAdapter(obj)
                    if quantity > item.quantity_max():
                        quantity = item.quantity_max()
                    if quantity > 0:
                        size = ISize(obj)
                        gross = item.gross()
                        kwargs = {
                            'depth': size.depth,
                            'gross': gross,
                            'height': size.height,
                            'net': item.get_net(gross),
                            'quantity': quantity,
                            'title': item.title(),
                            'sku': obj.sku,
                            'vat': item.get_vat(gross),
                            'vat_rate': item.context.vat_rate,
                            'weight': size.weight,
                            'width': size.width,
                        }
                        item.add_to_cart(**kwargs)
                        notify(ArticleAddedToCartEvent(item, self.request))
                    else:
                        message = _(u'Input positive integer value to add to cart.')
                else:
                    message = _(u"Not available to add to cart.")
            else:
                message = _(u"Input integer value to add to cart.")

            if message:
                IStatusMessage(self.request).addStatusMessage(message, type='warn')

            return self.request.response.redirect(url)


class CartArticleMultiAdapter(object):

    adapts(Interface, Interface)
    implements(ICartArticleMultiAdapter)

    def __init__(self, context, article):
        self.context = context
        self.article = article

    def orig_article(self):
        """Returns original article

        :rtype: collective.cart.core.Article
        """
        uuid = self.article['id']
        return IShoppingSite(self.context).get_object(UID=uuid)

    def image_url(self):
        """Returns image url of article

        :rtype: str
        """
        return IArticleAdapter(self.orig_article()).image_url()

    def gross_subtotal(self):
        """Returns money of article subtotal

        :rtype: moneyed.Money
        """
        return self.article['gross'] * self.article['quantity']

    def quantity_max(self):
        """Returns maximum size to be added to cart

        :rtype: int
        """
        return IStock(self.orig_article()).stock()

    def quantity_size(self):
        """Returns size of quantity for input size

        :rtype: int
        """
        return len(str(self.quantity_max()))
