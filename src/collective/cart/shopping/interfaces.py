from collective.behavior.price.interfaces import IPrice
from collective.cart import core
from collective.cart.core.interfaces import IArticleAdapter as IBaseArticleAdapter
from collective.cart.core.interfaces import ICartAdapter as IBaseCartAdapter
from collective.cart.core.interfaces import ICartArticle as IBaseCartArticle
from collective.cart.core.interfaces import ICartArticleAdapter as IBaseCartArticleAdapter
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
from zope.schema import Choice
from zope.schema import Decimal
from zope.schema import TextLine
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IShoppingSite(IBaseShoppingSite):
    """Adapter Interface for Shopping Site."""

    articles_total = Attribute('Total of articles in session')
    shipping_methods = Attribute('List of shipping methods')
    shipping_method = Attribute('Shipping method from cart')
    shipping_gross_money = Attribute('Gross money of shipping method in the session')
    shipping_vat_money = Attribute('VAT money of shipping method in the session')
    shipping_net_money = Attribute('Net money of shipping method in the session')
    total = Attribute('Total money')
    billing_same_as_shipping = Attribute('True if billing info in session cart is same as shipping info')
    is_addresses_filled = Attribute('True if addresses are filled')

    def locale():  # pragma: no cover
        """Returns locale for localizing money"""

    def format_money(money):  # pragma: no cover
        """Returns locale formated money

        :param money: Money
        :type money: moneyed.Money

        :rtype: unicode"""

    def locale_articles_total():  # pragma: no cover
        """Localized total money amount and currency of articles"""

    def get_shipping_gross_money(uuid):  # pragma: no cover
        """Get shipping gross money by uuid."""

    def locale_shipping_gross():  # pragma: no cover
        """Localized money amount and currency for shipping gross cost

        :rtype: unicode
        """

    def locale_total():  # pragma: no cover
        """Localized total amount and currency"""

    def update_shipping_method(uuid=None):  # pragma: no cover
        """Update shipping method of cart in session."""

    def get_address(self, name):  # pragma: no cover
        """Get address from cart in session."""

    def is_address_filled(value):  # pragma: no cover
        """Returns true if the address of the value is filled."""

    def get_info(self, name):
        """Get address info which could be used directy in form."""

    def get_brain_for_text(name):  # pragma: no cover
        """Get brain for displaying texts based on view name."""

    def update_address(name, data):  # pragma: no cover
        """Update address of cart in session.

        :param name: Name of address, such as billing and shipping.
        :type name: str

        :param data: Form data.
        :type data: dict

        :rtype: unicode or None
        """

    def reduce_stocks():  # pragma: no cover
        """Reduce stocks from articles"""

    def link_to_order_for_customer(number):  # pragma: no cover
        """Link to order for customer

        :param number: Cart ID
        :type number: int

        :rtype: str
        """


class IShoppingSiteMultiAdapter(Interface):
    """Multi adapter interface for updating cart."""

    def add_to_cart():  # pragma: no cover
        """Add to cart."""


class ICartArticleMultiAdapter(Interface):
    """Multi adapter interface for plone object and dictionary of cart article in session."""

    orig_article = Attribute('Original Article object')
    image_url = Attribute('Image url of the article')
    gross_subtotal = Attribute('Gross subtotal of the article')
    quantity_max = Attribute('Maximum quantity of the article in cart')
    quantity_size = Attribute('Size of quantity for input tag')


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


class IArticleAdapter(IBaseArticleAdapter):

    articles_in_article = Attribute('Articles in Article which is not optional subarticle.')
    subarticles = Attribute('Subarticles of the article.')
    subarticles_option = Attribute('Subarticles for form select option.')
    subarticle_addable_to_cart = Attribute('True if subarticles are addable to cart.')
    subarticle_soldout = Attribute('True or False for subarticle sold out.')
    subarticle_quantity_max = Attribute('Minimum max quantity for all the subarticles.')
    quantity_max = Attribute('Maximum quantity which could be added to cart')
    discount_available = Attribute('True if discount is available, else False.')
    discount_end = Attribute('End day of discount.')
    gross = Attribute('Gross money for the article.')
    vat = Attribute('VAT money for the article.')
    net = Attribute('Net money for the article.')
    soldout = Attribute('True or False for sold out.')
    image_url = Attribute('Image url of the article')
    title = Attribute('Title is inherited from parent if parent allow subarticles')


class ICart(core.interfaces.ICart):
    """Interface for Cart."""

    billing_same_as_shipping = Bool(
        title=_(u'Billing info same as shipping info'),
        required=False,
        default=True)


class ICartAdapter(IBaseCartAdapter):
    """Adapter interface for Cart"""

    articles_total = Attribute('Total money of the articles')
    shipping_method = Attribute('Brain of shipping method')
    shipping_gross_money = Attribute('Gross money of shipping method')
    shipping_net_money = Attribute('Net money of shipping method')
    shipping_vat_money = Attribute('VAT money of shipping method')
    articles_total = Attribute('Total money of articles')
    total = Attribute('Overall total money')

    def get_address(name):  # pragma: no cover
        """Get address by name."""


class ICartArticle(IBaseCartArticle):
    """Interface for CartArticle"""

    gross = Attribute('Gross money of CartArticle')
    net = Attribute('Net money of CartArticle')
    vat = Attribute('VAT money of CartArticle')
    quantity = Attribute('Quantity of CartArticle')


class ICartArticleAdapter(IBaseCartArticleAdapter):
    """Adapter interface for CartArticle"""

    gross_subtotal = Attribute('Gross subtotal')


class IBaseCustomerInfo(form.Schema):
    """Base Schema for all customer info."""

    first_name = TextLine(
        title=_(u'First Name'))

    last_name = TextLine(
        title=_(u'Last Name'))

    organization = TextLine(
        title=_(u'Organization'),
        required=False)

    vat = TextLine(
        title=_('VAT Number'),
        description=_(u'International VAT Number, for Finland it starts with FI.'),
        default=u'FI',
        required=False)

    email = TextLine(
        title=_(u'E-mail'))

    street = TextLine(
        title=_(u'Street Address'))

    post = TextLine(
        title=_(u'Post Code'),
        required=False)

    city = TextLine(
        title=_(u'City'))

    phone = TextLine(
        title=_(u'Phone Number'))


info_types = SimpleVocabulary([
    SimpleTerm(value=u'billing', title=_(u'Billing')), SimpleTerm(value=u'shipping', title=_(u'Shipping'))])


class ICustomerInfo(IBaseCustomerInfo):
    """Schema for collective.cart.shipping.CustomerInfo dexterity type."""

    orig_uuid = Attribute('Original UUID.')

    info_type = Choice(
        title=_(u'Type'),
        description=_(u'Select one if this information is used only for billing or shipping.'),
        vocabulary=info_types,
        required=False)


class IShop(core.interfaces.IShoppingSiteRoot):
    """Schema interface for shop."""


class IStockPrice(IPrice):

    price = Decimal(
        title=_(u"Price excluding VAT"),
        required=True)


alsoProvides(IStockPrice, form.IFormFieldProvider)


class ISubArticle(core.interfaces.IArticle):
    """Schema interface for variable."""


# Events


class IArticleAddedToCartEvent(Interface):
    """Event signaling when article is added to cart."""


class IBillingAddressConfirmedEvent(Interface):
    """Event signaling when billing address is confirmed."""


class IShippingAddressConfirmedEvent(Interface):
    """Event signaling when shipping address is confirmed."""


# Utilities


class IPriceUtility(Interface):
    """Utility interface for price."""


class IMoneyUtility(Interface):
    """Utility interface for money."""

    def __call__(money, currency=None, decimal=2):
        """Convert money to the currency with proper decimal point.

        :param money: Money object
        :type money: moneyed.Money,

        :param currency: Currency code or None
        :type currency: str or None

        :param decimal: Decimal point
        :type decimal: int

        :rtype: moneyed.Money"""


class IUnicodeUtility(Interface):
    """Utility interface for unicode."""

    def safe_unicode():  # pragma: no cover
        """Returns unicode of value.

        :param value: Basestring
        :type value: basestring

        :param encoding: Character set
        :type encoding: str

        :rtype: unicode
        """

    def address(address, encoding):  # pragma: no cover
        """Format address

        :param address: Address information
        :type address: dictionary

        :param encoding: Character set
        :type encoding: str

        :rtype: unicode
        """


class ILocaleUtility(Interface):
    """Utility interface for locale code"""

    def __call__(code):  # pragma: no cover
        """Returns combined language code from single code.

        :param code: Single lower case language code
        :type code: str

        :rtype: str or None
        """
