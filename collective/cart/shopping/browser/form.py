from Products.CMFCore.utils import getToolByName
from collective.cart import shipping
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping import _
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IBaseCustomerInfo
from five import grok
from plone.dexterity.utils import createContentInContainer
from plone.directives import form
from z3c.form import button
from zope.component import getMultiAdapter


class BaseCustomerInfoForm(form.SchemaForm):
    grok.context(IShoppingSiteRoot)
    grok.require('zope2.View')

    ignoreContext = True
    schema = IBaseCustomerInfo


class BillingInfoForm(BaseCustomerInfoForm):
    grok.name('billling-info-form')

    form_type = 'billing'
    prefix = 'form.billing.'

    @button.buttonAndHandler(_(u'Submit'))
    def handleApply(self, action):
        data, errors = self.extractData()
        cart = IShoppingSite(self.context).cart
        billing = cart.get('billing')
        if billing is None:
            billing = createContentInContainer(
                cart, 'collective.cart.shopping.CustomerInfo', id='billing',
                checkConstraints=False, **data)
            if cart.get('shipping') is None:
                createContentInContainer(
                    cart, 'collective.cart.shopping.CustomerInfo', id='shipping',
                    checkConstraints=False, **data)
            context_state = getMultiAdapter(
                (self.context, self.request), name='plone_context_state')
            return self.redirect(context_state.current_base_url())
        else:
            for key in data:
                if getattr(billing, key) != data[key]:
                    setattr(billing, key, data[key])


class ShippingInfoForm(BaseCustomerInfoForm):
    grok.name('shipping-info-form')

    form_type = 'shipping'
    prefix = 'form.shipping.'

    @button.buttonAndHandler(_(u'Submit'))
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


@form.default_value(field=shipping.schema.IShippingMethodSchema['shipping_method'])
def default_shipping_method(data):
    shipping_uid = getattr(IShoppingSite(data.context).cart, 'shipping_uid', None)
    if not shipping_uid:
        shipping_methods = getattr(IShoppingSite(data.context), 'shipping_methods', None)
        if shipping_methods:
            shipping_uid = shipping_methods[0].UID
    return shipping_uid


class ShippingMethodForm(shipping.browser.form.ShippingMethodForm):
    grok.layer(ICollectiveCartShoppingLayer)

    schema = shipping.schema.IShippingMethodSchema

    @button.buttonAndHandler(_(u'Update'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return
        uuid = data.get('shipping_method')
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(UID=uuid)
        if brains:
            shipping_method = brains[0]
            cart = IShoppingSite(self.context).cart
            setattr(cart, 'shipping_uid', uuid)
            # setattr(cart, 'shipping_title', shipping_method.title)
