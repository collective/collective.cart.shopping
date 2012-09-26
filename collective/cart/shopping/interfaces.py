from collective.behavior import price
from collective.cart import core
from collective.cart.shopping import _
from plone.app.textfield import RichText
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import Attribute
from zope.interface import alsoProvides
from zope.schema import Decimal
from zope.schema import TextLine


class IShoppingSite(core.interfaces.IShoppingSite):
    """Adapter Interface for Shopping Site."""

    shipping_methods = Attribute('List of shipping methods.')


class IArticleContainer(form.Schema, IImageScaleTraversable):
    """Container for Articles."""


class IArticle(core.interfaces.IArticle, IImageScaleTraversable):

    image = NamedBlobImage(
        title=_(u'Representative Image'),
        description=_(u'The representative image of this article.'),
        required=False)

    text = RichText(
        title=_(u'Detailed information'),
        description=_(u'Further detailed information comes here.'),
        required=False)


class IArticleAdapter(core.interfaces.IArticleAdapter):

    discount_available = Attribute('True if discount is available, else False.')
    discount_end = Attribute('End day of discount.')
    gross = Attribute('Gross money for the article.')
    vat = Attribute('VAT money for the article.')
    net = Attribute('Net money for the article.')
    soldout = Attribute('True or False for sold out.')


class ICart(core.interfaces.ICart):

    shipping_title = Attribute('Title for selected shipping method.')
    shipping_uid = Attribute('UUID for selected shipping method.')
    shipping_gross = Attribute('Gross price for selected shipping method.')
    shipping_net = Attribute('Net price for selected shipping method.')
    shipping_vat = Attribute('VAT price for selected shipping method.')
    shipping_vat_rate = Attribute('VAT rate for selected shipping method.')


class ICartArticle(core.interfaces.ICartArticle):
    """"""


class IBaseCustomerInfo(form.Schema):
    """Base Schema for all customer info."""

    first_name = TextLine(
        title=_(u'First Name'))

    last_name = TextLine(
        title=_(u'Last Name'))

    organization = TextLine(
        title=_(u'Organization'))

    vat = TextLine(
        title=_('VAT Number'),
        description=_(u'International VAT Number, for Finland it starts with FI.'),
        default=u'FI')

    email = TextLine(
        title=_(u'E-mail'))

    address = TextLine(
        title=_(u'Street Address'))

    post_code = TextLine(
        title=_(u'Post Code'),
        required=False)

    city = TextLine(
        title=_(u'City'))

    phone = TextLine(
        title=_(u'Phone Number'))


@form.default_value(field=IBaseCustomerInfo['first_name'])
def default_first_name(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.first_name


@form.default_value(field=IBaseCustomerInfo['last_name'])
def default_last_name(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.last_name


@form.default_value(field=IBaseCustomerInfo['organization'])
def default_organization(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.organization


@form.default_value(field=IBaseCustomerInfo['vat'])
def default_vat(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.vat
    else:
        return u'FI'


@form.default_value(field=IBaseCustomerInfo['email'])
def default_email(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.email


@form.default_value(field=IBaseCustomerInfo['address'])
def default_address(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.address


@form.default_value(field=IBaseCustomerInfo['post_code'])
def default_post_code(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.post_code


@form.default_value(field=IBaseCustomerInfo['city'])
def default_city(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.city


@form.default_value(field=IBaseCustomerInfo['phone'])
def default_phone(data):
    cart = IShoppingSite(data.context).cart
    info = cart.get(data.view.form_type)
    if info:
        return info.phone


class ICustomerInfo(IBaseCustomerInfo):
    """Schema for collective.cart.shipping.CustomerInfo dexterity type."""

    info_type = TextLine(
        title=_(u'Info Type'))


class IShop(core.interfaces.IShoppingSiteRoot):
    """Schema interface for shop."""


class IStockPrice(price.interfaces.IPrice):

    price = Decimal(
            title=_(u"Price excluding VAT"),
            required=True)


alsoProvides(IStockPrice, form.IFormFieldProvider)
