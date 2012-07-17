from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
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

    @button.buttonAndHandler(u'Submit')
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

    @button.buttonAndHandler(u'Submit')
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
