from collective.base.interfaces import IAdapter
from collective.behavior.price.interfaces import IPrice
from collective.cart import core
from collective.cart.core.interfaces import IArticle as IBaseArticle
from collective.cart.core.interfaces import IArticleAdapter as IBaseArticleAdapter
from collective.cart.core.interfaces import IOrder as IBaseOrder
from collective.cart.core.interfaces import IOrderAdapter as IBaseOrderAdapter
from collective.cart.core.interfaces import IOrderArticle as IBaseOrderArticle
from collective.cart.core.interfaces import IShoppingSite as IBaseShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping import _
from collective.cart.shopping.schema import ArticleContainerSchema
from collective.cart.shopping.schema import ArticleSchema
from collective.cart.shopping.schema import CustomerInfoSchema
from collective.cart.shopping.schema import OrderArticleSchema
from collective.cart.shopping.schema import OrderSchema
from collective.cart.shopping.schema import ShopSchema
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.schema import Decimal


# Content type

class IArticleContainer(ArticleContainerSchema, IImageScaleTraversable):
    """Interface for content type: collective.cart.shopping.ArticleContainer"""


class IArticle(ArticleSchema, IBaseArticle, IImageScaleTraversable):
    """Interface for content type: collective.cart.core.Article"""


class IOrder(OrderSchema, IBaseOrder):
    """Interface for content type: collective.cart.core.Order"""


class IOrderArticle(OrderArticleSchema, IBaseOrderArticle):
    """Interface for content type: collective.cart.core.OrderArticle"""

    gross = Attribute('Gross money of CartArticle')
    net = Attribute('Net money of CartArticle')
    vat = Attribute('VAT money of CartArticle')
    quantity = Attribute('Quantity of CartArticle')


class ICustomerInfo(CustomerInfoSchema):
    """Interface for content type: collective.cart.shopping.CustomerInfo"""


class IShop(ShopSchema, IShoppingSiteRoot):
    """Interface for content type: collective.cart.shopping.Shop"""


# Deprecated

ICart = IOrder
ICartArticle = IOrderArticle


# Adapter

class IShoppingSite(IBaseShoppingSite):
    """Adapter Interface for shopping site"""

    def locale():  # pragma: no cover
        """Returns locale for localizing money

        :rtype: unicode
        """

    def format_money(money):  # pragma: no cover
        """Returns locale formated money

        :param money: Money
        :type money: moneyed.Money

        :rtype: unicode
        """

    def articles_total():  # pragma: no cover
        """Returns total money of articles in cart

        :rtype: moneyed.Money
        """

    def locale_articles_total():  # pragma: no cover
        """Returns localized total money amount and currency of articles in cart

        :rtype: unicode
        """

    def shipping_methods():  # pragma: no cover
        """Returns list of shipping methods

        :rtype: list
        """

    def shipping_method():  # pragma: no cover
        """Returns shipping method in cart"""

    def get_shipping_gross_money(uuid):  # pragma: no cover
        """Returns shipping gross money by uuid

        :rtype: moneyed.Money
        """

    def shipping_gross_money():  # pragma: no cover
        """Returns shipping gross money

        :rtype: moneyed.Money
        """

    def locale_shipping_gross():  # pragma: no cover
        """Returns localized money amount and currency for shipping gross cost

        :rtype: unicode
        """

    def shipping_vat_money():  # pragma: no cover
        """Returns shipping vat money

        :rtype: moneyed.Money
        """

    def shipping_net_money():  # pragma: no cover
        """Returns shipping net money

        :rtype: moneyed.Money
        """

    def total():  # pragma: no cover
        """Returns total money in cart

        :rtype: moneyed.Money
        """

    def locale_total():  # pragma: no cover
        """Returns localized total amount and currency

        :rtype: unicode
        """

    def update_shipping_method(uuid=None):  # pragma: no cover
        """Update shipping method of cart"""

    def get_address(name):  # pragma: no cover
        """Returns address by name

        :param name: 'billing' or 'shipping'
        :type name: str

        :rtype: dict
        """

    def is_address_filled(name):  # pragma: no cover
        """Returns True if the address of name is filled else False

        :rtype: bool
        """

    def billing_same_as_shipping():  # pragma: no cover
        """Returns True if billing cart is same as shipping

        :rtype: bool
        """

    def is_addresses_filled():  # pragma: no cover
        """Returns True if addresses in cart are filled else False

        :rtype: bool
        """

    def get_info(name):  # pragma: no cover
        """Returns dictionary of address info by name

        :param name: 'billing' or 'shipping'
        :param type: str

        :rtype: dict
        """

    def get_brain_for_text(name):  # pragma: no cover
        """Returns brain for displaying texts based on context name

        :param name: ID of context
        :type name: str

        :rtype: brain or None
        """

    def update_address(name, data):  # pragma: no cover
        """Update address of cart and return message if there are one

        :param name: Name of address, such as billing and shipping.
        :type name: str

        :param data: Form data.
        :type data: dict

        :rtype: unicode or None
        """

    def reduce_stocks():  # pragma: no cover
        """Reduce stocks from articles"""

    def link_to_order(order_id):  # pragma: no cover
        """Returns link to order

        :param order_id: Order ID
        :type order_id: str

        :rtype: str
        """


class IShoppingSiteMultiAdapter(Interface):
    """Multi adapter interface for shopping site"""

    def add_to_cart():  # pragma: no cover
        """Add article to cart"""


class ICartArticleMultiAdapter(Interface):
    """Multi adapter interface for plone object and dictionary of cart article"""

    def orig_article():  # pragma: no cover
        """Returns original article

        :rtype: collective.cart.core.Article
        """

    def image_url():  # pragma: no cover
        """Returns image url of article

        :rtype: str
        """

    def gross_subtotal():  # pragma: no cover
        """Returns money of article subtotal

        :rtype: moneyed.Money
        """

    def quantity_max():  # pragma: no cover
        """Returns maximum size to be added to cart

        :rtype: int
        """

    def quantity_size():  # pragma: no cover
        """Returns size of quantity for input size

        :rtype: int
        """


class IArticleAdapter(IBaseArticleAdapter):
    """Adapter interface for content type: collective.cart.core.Article"""

    def articles(salable=None, use_subarticle=None):
        """Returns brain of articles located directly under context"""

    def soldout():  # pragma: no cover
        """Returns True if sold out else False

        :rtype: bool
        """

    def subarticles():  # pragma: no cover
        """Returns subarticles for form select option

        :rtype: list
        """

    def quantity_max():  # pragma: no cover
        """"""

    def discount_available():  # pragma: no cover
        """"""

    def gross():  # pragma: no cover
        """"""

    def get_net(gross):  # pragma: no cover
        """"""

    def get_vat(gross):  # pragma: no cover
        """"""

    def image_url():  # pragma: no cover
        """"""

    def title():  # pragma: no cover
        """"""


class IOrderAdapter(IBaseOrderAdapter):
    """Adapter interface for content type: collective.cart.core.Order"""

    def articles_total():  # pragma: no cover
        """Returns total money of articles

        :rtype: moneyed.Money
        """

    def shipping_method():  # pragma: no cover
        """Returns brain of shipping method"""

    def locale_shipping_method():  # pragma: no cover
        """Returns dictionary of shipping method containing localized cost of it"""

    def total():  # pragma: no cover
        """Returns total money of order

        :rtype: moneyed.Money
        """

    def get_address(name):  # pragma: no cover
        """Return brain of address by name

        :param name: 'billing' or 'shipping'
        :type name: str
        """


class IOrderArticleAdapter(IAdapter):
    """Adapter interface for content type: collective.cart.core.OrderArticle"""

    # gross_subtotal = Attribute('Gross subtotal')


class IStockPrice(IPrice):

    price = Decimal(
        title=_(u"Price excluding VAT"),
        required=True)


alsoProvides(IStockPrice, IFormFieldProvider)


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

    def safe_unicode(value, encoding=None):  # pragma: no cover
        """Returns unicode of value

        :param value: Basestring
        :type value: basestring

        :param encoding: Character set
        :type encoding: str

        :rtype: unicode
        """

    def fullname(address, encoding=None):
        """Returns unicode formated full name

        :param address: Address information
        :type address: dictionary

        :param encoding: Character set
        :type encoding: str

        :rtype: unicode
        """

    def address(address, encoding):  # pragma: no cover
        """Returns unicode formated address

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
