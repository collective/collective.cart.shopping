from Products.ATContentTypes.interfaces import IATDocument
from Products.ATContentTypes.interfaces import IATFolder
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation import validation
from collective.behavior.price.interfaces import ICurrency
from collective.behavior.size.interfaces import ISize
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.adapter.interface import ShoppingSite as BaseShoppingSite
from collective.cart.shipping.interfaces import IShippingMethod
from collective.cart.shopping import _
from collective.cart.shopping.event import ArticleAddedToCartEvent
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IBaseCustomerInfo
from collective.cart.shopping.interfaces import ICartArticleMultiAdapter
from collective.cart.shopping.interfaces import ILocaleUtility
from collective.cart.shopping.interfaces import IPriceUtility
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IShoppingSiteMultiAdapter
from decimal import Decimal
from five import grok
from moneyed import Money
from moneyed.localization import DEFAULT
from moneyed.localization import format_money
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import modified
from zope.publisher.interfaces.browser import IBrowserRequest

import types


class ShoppingSite(BaseShoppingSite):
    """Adapter for shopping site"""
    grok.provides(IShoppingSite)

    def locale(self):
        """Returns locale for localizing money"""
        code = self.context.restrictedTraverse('@@plone_portal_state').locale().getLocaleID()
        return getUtility(ILocaleUtility)(code) or DEFAULT

    def format_money(self, money):
        """Returns locale formated money

        :param money: Money
        :type money: moneyed.Money

        :rtype: unicode"""
        return format_money(money, locale=self.locale())

    @property
    def articles_total(self):
        """Total money of articles"""
        registry = getUtility(IRegistry)
        currency = registry.forInterface(ICurrency).default_currency
        res = Money(0.00, currency=currency)
        for item in self.cart_article_listing:
            res += item['gross'] * item['quantity']
        return res

    def locale_articles_total(self):
        """Localized total money amount and currency of articles"""
        return self.format_money(self.articles_total)

    @property
    def shipping_methods(self):
        if self.shop:
            return self.get_brains(IShippingMethod, path=self.shop_path)

    @property
    def shipping_method(self):
        if self.cart:
            return self.cart.get('shipping_method')

    def _calculated_weight(self, rate=None):
        weight = 0.0

        if self.shipping_method and rate and isinstance(rate, float) and rate > 0.0:

            for article in self.cart_article_listing:
                weight_in_kg = article['weight'] / 1000.0
                dimension_weight = (article['depth'] * article['height'] * article['width'] / 10.0 ** 6) * rate
                if dimension_weight > weight_in_kg:
                    article_weight = dimension_weight
                else:
                    article_weight = weight_in_kg

                weight += article_weight * article['quantity']

        return weight

    def get_shipping_gross_money(self, uuid):
        """Get shipping gross money by uuid."""
        if self.shipping_methods:
            shipping_methods = [sm for sm in self.shipping_methods if sm.UID == uuid]
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

    @property
    def shipping_gross_money(self):
        if self.shipping_method:
            return self.get_shipping_gross_money(self.shipping_method['uuid'])

    def locale_shipping_gross(self):
        """Localized money amount and currency for shipping gross cost

        :rtype: unicode
        """
        return self.format_money(self.shipping_gross_money)

    @property
    def shipping_vat_money(self):
        if self.shipping_gross_money:
            currency = self.shipping_gross_money.currency
            money = Decimal(self.shipping_method['vat_rate']) / 100 * self.shipping_gross_money
            price = getUtility(IPriceUtility, name="string")(money.amount)
            return Money(Decimal(price), currency)

    @property
    def shipping_net_money(self):
        if self.shipping_gross_money:
            return self.shipping_gross_money - self.shipping_vat_money

    @property
    def total(self):
        total = self.articles_total
        if self.shipping_gross_money:
            total += self.shipping_gross_money
        return total

    def locale_total(self):
        """Localized total amount and currency"""
        return self.format_money(self.total)

    def update_shipping_method(self, uuid=None):
        if self.cart_articles:
            if self.shipping_methods:
                if uuid is None:
                    if not self.shipping_method:
                        shipping_method = self.shipping_methods[0]
                        items = {
                            'title': shipping_method.Title,
                            'uuid': shipping_method.UID,
                            'min_delivery_days': shipping_method.min_delivery_days,
                            'max_delivery_days': shipping_method.max_delivery_days,
                            'vat_rate': shipping_method.vat,
                            'weight_dimension_rate': shipping_method.weight_dimension_rate,
                        }
                    else:
                        items = self.shipping_method

                else:
                    smethods = [smethod for smethod in self.shipping_methods if smethod.UID == uuid]
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

                    items = self.shipping_method

                items['gross'] = self.shipping_gross_money
                items['net'] = self.shipping_net_money
                items['vat'] = self.shipping_vat_money

                self.update_cart('shipping_method', items)

            else:
                self.remove_from_cart('shipping_method')

    def get_address(self, name):
        """Get address by name."""
        if self.cart:
            return self.cart.get(name)

    def is_address_filled(self, value):
        """Return true if the address of the value is filled."""
        info = self.get_address(value)
        if info:
            names = [name for name in IBaseCustomerInfo.names() if IBaseCustomerInfo.get(name).required]
            for name in names:
                if info.get(name) is None:
                    return False
            return True
        else:
            return False

    @property
    def billing_same_as_shipping(self):
        if self.cart:
            return self.cart.get('billing_same_as_shipping')

    @property
    def is_addresses_filled(self):
        """True if billing addresses is filled and billing_same_as_shipping is True or
        both billing and shipping addresses are filled."""
        if self.cart:
            billing_filled = self.is_address_filled('billing')
            return (self.billing_same_as_shipping and billing_filled) or (
                self.is_address_filled('shipping') and billing_filled)

    def get_info(self, name):
        """Return dictonary of address info by name."""
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

    def create_cart(self, cart_id=None):
        """Create cart"""
        cart = super(ShoppingSite, self).create_cart(cart_id=cart_id)
        if cart is not None:
            if self.shipping_method:
                shipping_method = createContentInContainer(cart, 'collective.cart.shipping.CartShippingMethod',
                        checkConstraints=False, id="shipping_method", **self.shipping_method)
                modified(shipping_method)
            cart.billing_same_as_shipping = self.billing_same_as_shipping
            if self.get_address('billing'):
                billing = createContentInContainer(cart, 'collective.cart.shopping.CustomerInfo',
                        checkConstraints=False, id="billing", **self.get_address('billing'))
                modified(billing)
            if not cart.billing_same_as_shipping and self.get_address('shipping'):
                shipping = createContentInContainer(cart, 'collective.cart.shopping.CustomerInfo',
                        checkConstraints=False, id="shipping", **self.get_address('shipping'))
                modified(shipping)

        return cart

    def get_brain_for_text(self, name):
        brain = self.get_brain(IATFolder, path=self.shop_path, depth=1, id=name)
        if brain:
            return self.get_brain(IATDocument, path=brain.getPath(), depth=1)

    def update_address(self, name, data):
        """Update address of cart in session.

        :param name: Name of address, such as billing and shipping.
        :type name: str

        :param data: Form data.
        :type data: dict

        :rtype: unicode or None
        """
        message = None

        if not data.get('first_name'):
            message = _(u'First name is missing.')

        elif not data.get('last_name'):
            message = _(u'Last name is missing.')

        elif not data.get('email') or validation.validatorFor('isEmail')(data.get('email')) != 1:
            message = _(u'Invalid e-mail address.')

        elif not data.get('street'):
            message = _(u'Street address is missing.')

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
        for item in self.cart_article_listing:
            uuid = item['id']
            quantity = item['quantity']
            obj = self.get_object(UID=uuid)
            IStock(obj).sub_stock(quantity)
            modified(obj)

    def link_to_order_for_customer(self, number):
        """Link to order for customer

        :param number: Cart ID
        :type number: int

        :rtype: str
        """
        return self.get_cart(number).absolute_url()


class ShoppingSiteMultiAdapter(grok.MultiAdapter):

    grok.adapts(Interface, IBrowserRequest)
    grok.provides(IShoppingSiteMultiAdapter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def add_to_cart(self):
        form = self.request.form
        uuid = form.get('subarticle') or form.get('form.buttons.AddToCart')
        if uuid is not None:
            quantity = form.get('quantity')
            validate = validation.validatorFor('isInt')
            url = getMultiAdapter(
                (self.context, self.request), name='plone_context_state').current_base_url()
            message = None
            if quantity is not None and validate(quantity) == 1:
                quantity = int(quantity)
                if quantity >= 0:
                    shopping_site = IShoppingSite(self.context)
                    obj = shopping_site.get_object(UID=uuid)
                    if obj:
                        item = IArticleAdapter(obj)
                        if item.addable_to_cart:
                            if quantity > item.quantity_max:
                                quantity = item.quantity_max
                            if quantity > 0:
                                size = ISize(obj)
                                kwargs = {
                                    'depth': size.depth,
                                    'gross': item.gross,
                                    'height': size.height,
                                    'net': item.net,
                                    'quantity': quantity,
                                    'title': item.title,
                                    'sku': obj.sku,
                                    'vat': item.vat,
                                    'vat_rate': item.context.vat,
                                    'weight': size.weight,
                                    'width': size.width,
                                }
                                item.add_to_cart(**kwargs)
                                notify(ArticleAddedToCartEvent(item, self.request))
                                return self.request.response.redirect(url)
                    message = _(u'Not available to add to cart.')
                else:
                    message = _(u"Input positive integer value to add to cart.")
            else:
                message = _(u"Input integer value to add to cart.")

            if message:
                IStatusMessage(self.request).addStatusMessage(message, type='warn')

            return self.request.response.redirect(url)


class CartArticleMultiAdapter(grok.MultiAdapter):

    grok.adapts(Interface, Interface)
    grok.provides(ICartArticleMultiAdapter)

    def __init__(self, context, article):
        self.context = context
        self.article = article

    @property
    def orig_article(self):
        """Returns original Article object."""
        uuid = self.article['id']
        return IShoppingSite(self.context).get_object(UID=uuid)

    @property
    def image_url(self):
        """Returns image url of the article.
        If the image does not exists then return from parent or fallback image.
        """
        return IArticleAdapter(self.orig_article).image_url

    @property
    def locale_gross(self):
        code = self.context.restrictedTraverse('@@plone_portal_state').locale().getLocaleID()
        locale = getUtility(ILocaleUtility)(code) or DEFAULT
        return format_money(self.article['gross'], locale=locale)

    @property
    def locale_gross_subtotal(self):
        code = self.context.restrictedTraverse('@@plone_portal_state').locale().getLocaleID()
        locale = getUtility(ILocaleUtility)(code) or DEFAULT
        return format_money((self.article['gross'] * self.article['quantity']), locale=locale)

    @property
    def gross_subtotal(self):
        return self.article['gross'] * self.article['quantity']

    @property
    def quantity_max(self):
        return IStock(self.orig_article).stock

    @property
    def quantity_size(self):
        return len(str(self.quantity_max))
