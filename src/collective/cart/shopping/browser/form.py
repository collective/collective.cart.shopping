from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping import _
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IBaseCustomerInfo
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.schema import IShippingMethodSchema
from five import grok
from plone.dexterity.utils import createContentInContainer
from plone.directives import form
from z3c.form import button
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.lifecycleevent import modified


class BaseCustomerInfoForm(form.SchemaForm):
    grok.context(IShoppingSiteRoot)
    grok.require('zope2.View')

    ignoreContext = True
    schema = IBaseCustomerInfo


class BillingInfoForm(BaseCustomerInfoForm):
    grok.name('billling-info-form')

    form_type = 'billing'
    prefix = 'form.billing.'

    @button.buttonAndHandler(_(u'Save Info'), name='submit')
    def handleApply(self, action):
        data, errors = self.extractData()
        cart = IShoppingSite(self.context).cart
        billing = cart.get('billing')
        if billing is None:
            billing = createContentInContainer(
                cart, 'collective.cart.shopping.CustomerInfo', id='billing',
                checkConstraints=False, **data)
            if cart.get('shipping') is None:
                shipping = createContentInContainer(cart, 'collective.cart.shopping.CustomerInfo',
                    id='shipping', checkConstraints=False, **data)
                modified(shipping)

        else:
            for key in data:
                if getattr(billing, key) != data[key]:
                    setattr(billing, key, data[key])

        modified(billing)
        context_state = getMultiAdapter(
            (self.context, self.request), name='plone_context_state')
        return self.redirect(context_state.current_base_url())


class ShippingInfoForm(BaseCustomerInfoForm):
    grok.name('shipping-info-form')

    form_type = 'shipping'
    prefix = 'form.shipping.'

    @button.buttonAndHandler(_(u'Save Info'), name='submit')
    def handleApply(self, action):
        data, errors = self.extractData()
        cart = IShoppingSite(self.context).cart
        shipping = cart.get('shipping')
        if shipping is None:
            shipping = createContentInContainer(
                cart, 'collective.cart.shopping.CustomerInfo', id='shippings',
                checkConstraints=False, **data)
        else:
            for key in data:
                if getattr(shipping, key) != data[key]:
                    setattr(shipping, key, data[key])

        modified(shipping)
        context_state = getMultiAdapter(
            (self.context, self.request), name='plone_context_state')
        return self.redirect(context_state.current_base_url())


@form.default_value(field=IShippingMethodSchema['shipping_method'])
def default_shipping_method(data):
    if IShoppingSite(data.context).shipping_method:
        shipping_uuid = IShoppingSite(data.context).shipping_method.orig_uuid
    else:
        shipping_uuid = IShoppingSite(data.context).shipping_methods[0].UID
    return shipping_uuid


class ShippingMethodForm(form.SchemaForm):
    grok.context(Interface)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('shipping-method-form')
    grok.require('zope2.View')

    ignoreContext = True
    schema = IShippingMethodSchema

    @button.buttonAndHandler(_(u'Update'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return
        uuid = data.get('shipping_method')
        cart = IShoppingSite(self.context).cart
        ICartAdapter(cart).update_shipping_method(uuid=uuid)
