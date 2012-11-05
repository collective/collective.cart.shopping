from collective.behavior.price.interfaces import IPrice
from collective.cart import core
from collective.cart.core.interfaces import IShoppingSite as IBaseShoppingSite
from collective.cart.shopping import _
from plone.app.textfield import RichText
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.schema import Bool
from zope.schema import Decimal
from zope.schema import TextLine


class IShoppingSite(IBaseShoppingSite):
    """Adapter Interface for Shopping Site."""

    shipping_methods = Attribute('List of shipping methods')
    shipping_method = Attribute('Shipping method from cart')
    total = Attribute('Total money')


class IUpdateCart(Interface):
    """Multi adapter interface for updating cart."""

    def add_to_cart(uuid):
        """Add to cart."""

    def update_cart(uuid):
        """Update cart."""


class IArticleContainer(form.Schema, IImageScaleTraversable):
    """Container for Articles."""


class IArticle(core.interfaces.IArticle, IImageScaleTraversable):

    use_subarticle = Bool(
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

    image_url = Attribute('URL of Image.')
    title = Attribute('Title of article could be inherited from parent...')


class IArticleAdapter(core.interfaces.IArticleAdapter):

    articles_in_article = Attribute('Articles in Article which is not optional subarticle.')
    discount_available = Attribute('True if discount is available, else False.')
    discount_end = Attribute('End day of discount.')
    gross = Attribute('Gross money for the article.')
    net = Attribute('Net money for the article.')
    soldout = Attribute('True or False for sold out.')
    subarticle_addable_to_cart = Attribute('True if subarticles are addable to cart.')
    subarticle_quantity_max = Attribute('Minimum max quantity for all the subarticles.')
    subarticle_soldout = Attribute('True or False for subarticle sold out.')
    subarticles = Attribute('Subarticles of the article.')
    subarticles_option = Attribute('Subarticles for form select option.')
    vat = Attribute('VAT money for the article.')


class ICart(core.interfaces.ICart):
    """Interface for Cart."""


class ICartAdapter(core.interfaces.ICartAdapter):
    """Adapter interface for Cart"""

    # billing_info = Attribute('Billing info')
    # shipping_info = Attribute('Shipping info')
    articles_total = Attribute('Total money of articles')
    shipping_method = Attribute('Brain of shipping method')
    shipping_gross_money = Attribute('Gross money of shipping method')
    shipping_net_money = Attribute('Net money of shipping method')
    shipping_vat_money = Attribute('VAT money of shipping method')

    def update_shipping_method(uuid=None):  # pragma: no cover
        """Update shipping method based on uuid."""


class ICartArticle(core.interfaces.ICartArticle):
    """Interface for CartArticle"""

    gross = Attribute('Gross money of CartArticle')
    net = Attribute('Net money of CartArticle')
    vat = Attribute('VAT money of CartArticle')
    quantity = Attribute('Quantity of CartArticle')
    weight = Attribute('Weight of CartArticle')
    height = Attribute('Height of CartArticle')
    width = Attribute('Width of CartArticle')
    depth = Attribute('Depth of CartArticle')


class ICartArticleAdapter(core.interfaces.ICartArticleAdapter):
    """Adapter interface for CartArticle"""

    gross_subtotal = Attribute('Gross subtotal')


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


class IStockPrice(IPrice):

    price = Decimal(
        title=_(u"Price excluding VAT"),
        required=True)


alsoProvides(IStockPrice, form.IFormFieldProvider)


class ISubArticle(core.interfaces.IArticle):
    """Schema interface for variable."""
