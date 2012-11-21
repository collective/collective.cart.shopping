from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cart.shopping.browser.form import ShippingMethodForm
from plone.z3cform.layout import FormWrapper


class CustomerInfoFormWrapper(FormWrapper):
    """Form wrapper for customer info viewlet."""

    index = ViewPageTemplateFile('viewlets/customer-info-formwrapper.pt')


class ShippingMethodFormWrapper(FormWrapper):

    form = ShippingMethodForm
    index = ViewPageTemplateFile("viewlets/formwrapper.pt")
