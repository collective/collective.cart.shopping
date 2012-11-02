from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from collective.behavior.size.interfaces import ISize
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.adapter import interface
from collective.cart.shipping.interfaces import IShippingMethod
from collective.cart.shopping import _
from collective.cart.shopping import interfaces
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import ICartAdapter
from five import grok
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


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
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        query = {
                'path': '/'.join(self.shop.getPhysicalPath()),
                'object_provides': IShippingMethod.__identifier__,
            }
        return catalog(query)

    @property
    def shipping_method(self):
        return ICartAdapter(self.cart).shipping_method


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
                                    'gross': item.gross,
                                    'net': item.net,
                                    'vat': item.vat,
                                    'vat_rate': item.context.vat,
                                    'quantity': quantity,
                                    'weight': size.weight,
                                    'width': size.width,
                                    'height': size.height,
                                    'depth': size.depth,
                                }
                                item.add_to_cart(**kwargs)
                                IStock(obj).sub_stock(quantity)
                        except ValueError:
                            message = _(u"Input integer value to add to cart.")
                            IStatusMessage(self.request).addStatusMessage(message, type='warn')
                        finally:
                            return self.request.response.redirect(url)
