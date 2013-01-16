from Acquisition import aq_inner
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from collective.behavior.price.interfaces import ICurrency
from collective.behavior.size.interfaces import ISize
from collective.behavior.stock.interfaces import IStock
from collective.cart import core
from collective.cart.shipping.interfaces import ICartShippingMethod
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IBaseCustomerInfo
from collective.cart.shopping.interfaces import ICart
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICartArticle
from collective.cart.shopping.interfaces import ICartArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from decimal import Decimal
from five import grok
from moneyed import Money
from plone.app.contentlisting.interfaces import IContentListing
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.lifecycleevent import modified

import types


class CartAdapter(core.adapter.cart.CartAdapter):
    """Adapter for Cart"""

    grok.context(ICart)
    grok.provides(ICartAdapter)

    @property
    def articles(self):
        """List of dictionary of Articles within cart."""
        encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        res = []
        for item in IContentListing(self.get_brains(ICartArticle)):
            obj = item.getObject()
            items = {
                # 'description': item.Description(),
                'description': item.Description().decode(encoding),
                'gross': item.gross,
                'gross_subtotal': ICartArticleAdapter(obj).gross_subtotal,
                'id': item.getId(),
                'image_url': None,
                'obj': obj,
                'quantity': item.quantity,
                'quantity_max': item.quantity,
                'sku': item.sku,
                # 'title': item.Title(),
                'title': item.Title().decode(encoding),
                'url': None,
                'vat_rate': item.vat_rate,
            }
            orig_article = ICartArticleAdapter(obj).orig_article
            if orig_article:
                items['url'] = orig_article.absolute_url()
                items['image_url'] = IArticleAdapter(orig_article).image_url
                items['quantity_max'] += IStock(orig_article).stock
            items['quantity_size'] = len(str(items['quantity_max']))
            res.append(items)
        return res

    @property
    def articles_total(self):
        """Total money of articles"""
        registry = getUtility(IRegistry)
        currency = registry.forInterface(ICurrency).default_currency
        res = Money(0.00, currency=currency)
        for item in self.articles:
            res += item['gross'] * item['quantity']
        return res

    @property
    def total(self):
        total = self.articles_total
        if self.shipping_gross_money:
            total += self.shipping_gross_money
        return total

    @property
    def shipping_method(self):
        """Brain of shipping method of the cart."""
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        query = {
            'object_provides': ICartShippingMethod.__identifier__,
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'depth': 1,
            },
        }
        brains = catalog(query)
        if brains:
            return brains[0]

    def _calculated_weight(self, rate=None):
        weight = 0
        for article in self.articles:
            obj = article['obj']
            weight += ISize(obj).calculated_weight(rate=rate) * article['quantity']
        return weight

    @property
    def shipping_gross_money(self):
        if self.shipping_method:
            shipping_methods = [sm for sm in IShoppingSite(self.context).shipping_methods if sm.UID == self.shipping_method.orig_uuid]
            if shipping_methods:
                shipping_method = shipping_methods[0]
                obj = shipping_method.getObject()
                rate = shipping_method.weight_dimension_rate
                shipping_fee = price = obj.shipping_fee()
                if isinstance(shipping_fee, types.FunctionType):
                    price = shipping_fee(self._calculated_weight(rate=rate))
                registry = getUtility(IRegistry)
                currency = registry.forInterface(ICurrency).default_currency
                return Money(price, currency=currency)

    @property
    def shipping_net_money(self):
        if self.shipping_gross_money:
            return self.shipping_gross_money - self.shipping_vat_money

    @property
    def shipping_vat_money(self):
        if self.shipping_gross_money:
            return Decimal(self.shipping_method.vat_rate) / 100 * self.shipping_gross_money

    @property
    def billing_info(self):
        return self.get_address('billing')

    @property
    def shipping_info(self):
        return self.get_address('shipping')

    def is_address_filled(self, name):
        """Return true if the address of the name is filled."""
        info = self.get_address(name)
        names = [name for name in IBaseCustomerInfo.names() if IBaseCustomerInfo.get(name).required]
        for name in names:
            if getattr(info, name, None) is None:
                return False
        return True

    @property
    def is_addresses_filled(self):
        """True if both billing and shipping addresses are filled."""
        return self.is_address_filled('billing') and self.is_address_filled('shipping')

    def add_address(self, name):
        """Add address with name."""

    def add_addresses(self):
        pass

    def get_address(self, name):
        """Get address by name."""
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        query = {
            'id': name,
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'depth': 1,
            }
        }
        brains = catalog(query)
        if brains:
            return brains[0]

    def update_address(self, name, data):
        """Update existing address."""
        address = self.get_address(name).getObject()
        for attr in IBaseCustomerInfo.names():
            value = getattr(data, attr, None) or data.get(attr)
            setattr(address, attr, value)
        address.orig_uuid = getattr(data, 'UID', None)
        modified(address)

    def update_shipping_method(self, uuid=None):
        context = aq_inner(self.context)
        if self.articles:
            shipping_methods = IShoppingSite(context).shipping_methods
            if uuid is None:
                if shipping_methods and not self.shipping_method:
                    shipping_method = shipping_methods[0]
                    sm = createContentInContainer(context, 'collective.cart.shipping.CartShippingMethod',
                        id='shipping_method', checkConstraints=False,
                        title=shipping_method.Title,
                        orig_uuid=shipping_method.UID,
                        min_delivery_days=shipping_method.min_delivery_days,
                        max_delivery_days=shipping_method.max_delivery_days,
                        vat_rate=shipping_method.vat,
                        weight_dimension_rate=shipping_method.weight_dimension_rate)
                    modified(sm)
                    sm.gross = self.shipping_gross_money
                    sm.net = self.shipping_net_money
                    sm.vat = self.shipping_vat_money
                    modified(sm)
                elif self.shipping_method:
                    sm = self.shipping_method.getObject()
                    sm.gross = self.shipping_gross_money
                    sm.net = self.shipping_net_money
                    sm.vat = self.shipping_vat_money
                    modified(sm)
            else:
                if self.shipping_method:
                    if uuid == self.shipping_method.orig_uuid:
                        sm = self.shipping_method.getObject()
                        sm.gross = self.shipping_gross_money
                        sm.net = self.shipping_net_money
                        sm.vat = self.shipping_vat_money
                        modified(sm)
                    else:
                        smethods = [smethod for smethod in shipping_methods if smethod.UID == uuid]
                        if smethods:
                            shipping_method = smethods[0]
                            sm = self.shipping_method.getObject()
                            sm.orig_uuid = uuid
                            sm.title = shipping_method.Title
                            sm.min_delivery_days = shipping_method.min_delivery_days
                            sm.max_delivery_days = shipping_method.max_delivery_days
                            sm.vat_rate = shipping_method.vat
                            sm.weight_dimension_rate = shipping_method.weight_dimension_rate
                            modified(sm)
                else:
                    smethods = [smethod for smethod in shipping_methods if smethod.UID == uuid]
                    if smethods:
                        shipping_method = smethods[0]
                        sm = createContentInContainer(context, 'collective.cart.shipping.CartShippingMethod',
                            id='shipping_method', checkConstraints=False,
                            title=shipping_method.Title,
                            orig_uuid=uuid,
                            min_delivery_days=shipping_method.min_delivery_days,
                            max_delivery_days=shipping_method.max_delivery_days,
                            vat_rate=shipping_method.vat,
                            weight_dimension_rate=shipping_method.weight_dimension_rate)
                        modified(sm)
                        sm.gross = self.shipping_gross_money
                        sm.net = self.shipping_net_money
                        sm.vat = self.shipping_vat_money
                        modified(sm)
