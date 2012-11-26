from Products.ATContentTypes.interfaces import IATDocument
from Products.ATContentTypes.interfaces import IATFolder
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from collective.behavior.price.interfaces import ICurrency
from collective.behavior.size.interfaces import ISize
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.adapter import interface
from collective.cart.shipping.interfaces import IShippingMethod
from collective.cart.shopping import _
from collective.cart.shopping import interfaces
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import ICartAdapter
from five import grok
from moneyed import Money
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

import types


class ShoppingSite(interface.ShoppingSite):

    grok.provides(interfaces.IShoppingSite)

    @property
    def articles_total(self):
        return ICartAdapter(self.cart).articles_total

    @property
    def total(self):
        return ICartAdapter(self.cart).total

    @property
    def shipping_methods(self):
        path = '/'.join(self.shop.getPhysicalPath())
        return self.get_brains(IShippingMethod, path=path)

    @property
    def shipping_method(self):
        return ICartAdapter(self.cart).shipping_method

    def get_shipping_gross_money(self, uuid):
        """Get shipping gross money by uuid."""
        shipping_methods = [sm for sm in self.shipping_methods if sm.UID == uuid]
        if shipping_methods:
            shipping_method = shipping_methods[0]
            obj = shipping_method.getObject()
            rate = shipping_method.weight_dimension_rate
            shipping_fee = price = obj.shipping_fee()
            if isinstance(shipping_fee, types.FunctionType):
                price = shipping_fee(ICartAdapter(self.cart)._calculated_weight(rate=rate))
            registry = getUtility(IRegistry)
            currency = registry.forInterface(ICurrency).default_currency
            return Money(price, currency=currency)

    def get_brain_for_text(self, name):
        path = '/'.join(self.shop.getPhysicalPath())
        brains = self.get_brains(IATFolder, path=path, depth=1, id=name)
        if brains:
            brain = brains[0]
            brains = self.get_brains(IATDocument, path=brain.getPath(), depth=1)
            if brains:
                return brains[0]


class UpdateCart(grok.MultiAdapter):

    grok.adapts(Interface, IBrowserRequest)
    grok.provides(interfaces.IUpdateCart)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def add_to_cart(self):
        form = self.request.form
        uuid = form.get('subarticle') or form.get('form.buttons.AddToCart')
        if uuid is not None:
            portal_state = getMultiAdapter((self.context, self.request), name="plone_portal_state")
            if portal_state.anonymous():
                url = '{}/login'.format(portal_state.portal_url())
                return self.request.response.redirect(url)
            quantity = form.get('quantity')
            if quantity is not None:
                brains = getToolByName(self.context, 'portal_catalog')(UID=uuid)
                if brains:
                    obj = brains[0].getObject()
                    item = IArticleAdapter(obj)
                    if item.addable_to_cart:
                        url = getMultiAdapter(
                            (self.context, self.request), name='plone_context_state').current_base_url()
                        try:
                            quantity = int(quantity)
                            if quantity > 0:
                                if quantity > item.quantity_max:
                                    quantity = item.quantity_max
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
                                IStock(obj).sub_stock(quantity)
                        except ValueError:
                            message = _(u"Input integer value to add to cart.")
                            IStatusMessage(self.request).addStatusMessage(message, type='warn')
                        finally:
                            return self.request.response.redirect(url)
