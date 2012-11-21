from collective.cart.shopping import _
from plone.directives import form
from zope import schema


class IShippingMethodSchema(form.Schema):

    shipping_method = schema.Choice(
        title=_(u'Shipping Method'),
        required=True,
        vocabulary=u"collective.cart.shipping.methods")
