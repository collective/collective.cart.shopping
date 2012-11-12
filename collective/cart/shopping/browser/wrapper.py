from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cart.shipping.browser import wrapper
from collective.cart.shopping.browser.form import ShippingMethodForm
from plone.z3cform.layout import FormWrapper


class ShippingMethodFormWrapper(wrapper.ShippingMethodFormWrapper):
    form = ShippingMethodForm


class CustomerInfoFormWrapper(FormWrapper):
    """Form wrapper for customer info viewlet."""

    index = ViewPageTemplateFile('viewlets/customer-info-formwrapper.pt')
