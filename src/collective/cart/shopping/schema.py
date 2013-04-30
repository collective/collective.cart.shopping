from collective.cart.core.schema import ArticleSchema as BaseArticleSchema
from collective.cart.core.schema import OrderSchema as BaseOrderSchema
from collective.cart.core.schema import OrderArticleSchema as BaseOrderArticleSchema
from collective.cart.shopping import _
from collective.cart.shopping.vocabulary import info_types
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.supermodel.model import Schema
from zope import schema


class ShopSchema(Schema):
    """Schema for content type: collective.cart.shopping.Shop"""


class ArticleContainerSchema(Schema):
    """Schema for content type: collective.cart.shopping.ArticleContainer"""


class ArticleSchema(BaseArticleSchema):
    """Schema for content type: collective.cart.core.Article"""

    use_subarticle = schema.Bool(
        title=_(u'Use Subarticle'),
        description=_(u'Check if this article has options such as sizes and colors.'),
        required=False)

    image = NamedBlobImage(
        title=_(u'Representative Image'),
        description=_(u'The representative image of this article.'),
        required=False)

    text = RichText(
        title=_(u'Detailed information'),
        description=_(u'Further detailed information comes here.'),
        required=False)


class OrderSchema(BaseOrderSchema):
    """Schema for content type: collective.cart.core.Order"""

    billing_same_as_shipping = schema.Bool(
        title=_(u'Billing info same as shipping info'),
        required=False,
        default=True)


class OrderArticleSchema(BaseOrderArticleSchema):
    """Schema for content type: collective.cart.core.OrderArticle"""


class CustomerInfoSchema(Schema):
    """Schema for content type: collective.cart.shopping.CustomerInfo"""

    first_name = schema.TextLine(
        title=_(u'First Name'))

    last_name = schema.TextLine(
        title=_(u'Last Name'))

    organization = schema.TextLine(
        title=_(u'Organization'),
        required=False)

    vat = schema.TextLine(
        title=_('VAT Number'),
        description=_(u'International VAT Number, for Finland it starts with FI.'),
        default=u'FI',
        required=False)

    email = schema.TextLine(
        title=_(u'E-mail'))

    street = schema.TextLine(
        title=_(u'Street Address'))

    post = schema.TextLine(
        title=_(u'Post Code'))

    city = schema.TextLine(
        title=_(u'City'))

    phone = schema.TextLine(
        title=_(u'Phone Number'))

    info_type = schema.Choice(
        title=_(u'Type'),
        description=_(u'Select one if this information is used only for billing or shipping.'),
        vocabulary=info_types,
        required=False)
