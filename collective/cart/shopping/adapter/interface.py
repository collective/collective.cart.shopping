from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from collective.cart.core.adapter import interface
from collective.cart.shipping.interfaces import IShippingMethod
from collective.cart.shopping import interfaces
from collective.cart.shopping.interfaces import ICartAdapter
from five import grok


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
