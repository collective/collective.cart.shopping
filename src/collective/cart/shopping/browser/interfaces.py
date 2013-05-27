from collective.base.interfaces import IBaseFormView
from collective.base.interfaces import IRepeatedViewletManager
from collective.base.interfaces import IViewlet
from collective.cart.core.browser.interfaces import IAddToCartViewlet as IBaseBaseAddToCartViewlet
from collective.cart.core.browser.interfaces import ICartArticleListingViewlet
from collective.cart.core.browser.interfaces import ICheckOutView as IBaseCheckOutView
from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import Attribute
from zope.viewlet.interfaces import IViewletManager


# Browser layer

class ICollectiveCartShoppingLayer(ICollectiveCartCoreLayer):
    """Marker interface for browserlayer."""


# Viewlet manager

class IArticleContainerViewletManager(IViewletManager):
    """Viewlet manager interface for content type: collective.cart.shopping.ArticleContainer"""


class IOrderListingViewletManager(IRepeatedViewletManager):
    """Viewlet manager interface for order listing"""


# View

class IBaseArticleView(IBaseFormView):
    """View interface for BaseArticleView"""

    def adapter():
        """Returns ArticleAdapter"""


class IArticleView(IBaseArticleView):
    """View interface for ArticleView"""


class IStockView(IBaseArticleView):
    """View interface for StockView"""

    def stock():
        """Returns stock

        :rtype: int
        """

    def stocks():
        """Returns content listing of stock"""


class IArticleContainerView(IViewView):
    """View interface for ArticleContainerView"""


class ICheckOutView(IBaseCheckOutView):
    """View interface for check out"""

    def shopping_site():
        """Returns adapter: ShoppingSite

        :rtype: collective.cart.shopping.adapter.interface.ShoppingSite
        """

    def cart_articles():
        """Returns articles in cart

        :rtype: dict
        """


class ICartView(ICheckOutView):
    """View interface for cart"""


class IBillingAndShippingView(ICheckOutView):
    """View interface for billing and shipping"""


class IOrderConfirmationView(ICheckOutView):
    """View interface for order confirmation"""


class IThanksView(ICheckOutView):
    """View interface for thanks"""


class IArticleListingView(IBaseFormView):
    """View interface for article listing"""

    def table_headers():
        """Returns headers for table

        :rtype: tuple
        """

    def articles():
        """Returns list of dictionary of articles in shop

        :rtype: list
        """


class ICustomerInfoView(IViewView):
    """View interface for CustomerInfoView"""


class IBaseOrderMailTemplateView(IViewView):
    """Base view interface for order mail template"""

    is_for_customer = Attribute('True or False')

    def message():
        """Returns message converted from html to text

        :rtype: str
        """

    def link_to_order():
        """Returns link to order

        :rtype: str
        """


class IToCustomerOrderMailTemplateView(IBaseOrderMailTemplateView):
    """View interface for ToCustomerOrderMailTemplateView"""


class IToShopOrderMailTemplateView(IBaseOrderMailTemplateView):
    """View interface for ToShopOrderMailTemplateView"""


# Viewlet

class IArticlesInArticleContainerViewlet(IViewlet):
    """Viewlet interface for ArticlesInArticleContainerViewlet"""


class IBaseArticleViewlet(IViewlet):
    """Viewlet interface for BaseArticleViewlet"""

    def title():
        """Returns title"""


class IArticleImagesViewlet(IBaseArticleViewlet):
    """Viewlet interface for ArticleImagesViewlet"""

    def images():
        """Returns images"""

    def image_url():
        """Returns image url"""


class IBaseAddToCartViewlet(IBaseArticleViewlet, IBaseBaseAddToCartViewlet):
    """Viewlet interface for BaseAddToCartViewlet"""

    def quantity_size():
        """Returns size for quantity field

        :rtype: int
        """


class IAddToCartViewlet(IBaseAddToCartViewlet):
    """Viewlet interface for AddToCartViewlet"""

    def quantity_max():
        """Max quantity

        :rtype: int
        """

    def soldout():
        """Returns True if sold out else False

        :rtype: bool
        """

    def available():
        """Returns True if available else False

        :rtype: bool
        """

    def uuid():
        """Returns uuid

        :rtype: str
        """

    def gross():
        """Returns localized discount money or original gross money

        :rtype: unicode
        """

    def money():
        """Returns localized original gross money

        :rtype: unicode
        """

    def vat_rate():
        """Returns localized VAT rate

        :rtype: unicode
        """

    def discount_available():
        """Returns True if discount is available else False

        :rtype: bool
        """

    def discount_end():
        """Returns end of date for discount

        :rtype: unicode
        """

    def subarticles():
        """Returns list of subarticles

        :rtype: list
        """

    def articles():
        """Returns brains of articles

        :rtype: brains
        """

    def display_stock():
        """Returns True if displaying stock else False

        :rtype: bool
        """


class IArticlesInArticleViewlet(IAddToCartViewlet):
    """Viewlet interface for ArticlesInArticleViewlet"""

    def available():
        """Returns True if available else False

        :rtype: bool
        """

    def articles():
        """Returns list of dictionary of articles

        :rtype: list
        """


class IRelatedArticlesViewlet(IViewlet):
    """Viewlet interface for RelatedArticlesViewlet"""

    def articles():
        """Returns list of dictionary of articles

        :rtype: list
        """


class IAddSubtractStockViewlet(IBaseArticleViewlet):
    """Viewlet interface for AddSubtractStockViewlet"""

    def stock():
        """Returns stock

        :rtype: int
        """

    def stocks():
        """Returns list of dictionary of stocks

        :rtype: list
        """

    def add():
        """Returns attributes: max and size for input: add

        :rtype: dict
        """

    def subtract():
        """Returns attributes: max and size for input: subtract

        :rtype: dict
        """


class IStockListingViewlet(IViewlet):
    """Viewlet interface for StockListingViewlet"""

    def stocks():
        """Returns list of dictionary of stocks

        :rtype: list
        """


class ICheckOutFlowViewlet(IViewlet):
    """Viewlet interface for CheckOutFlowViewlet"""

    def items():
        """Returns list of dictionary of check out component

        :rtype: list
        """


class IBaseCheckOutButtonsViewlet(IViewlet):
    """Viewlet interface for BaseCheckOutButtonsViewlet"""

    def buttons():
        """Returns list of dictionary of buttons

        :rtype: list
        """

    def available():
        """Returns True if available else False

        :rtype: bool
        """


class ICartArticlesTotalViewlet(IViewlet):
    """Viewlet interface for CartArticlesTotalViewlet"""

    def articles_total():
        """Returns localized money of articles total

        :rtype: unicode
        """

    def available():
        """Returns True if articles in cart else False

        :rtype: bool
        """


class ICartCheckOutButtonsViewlet(IBaseCheckOutButtonsViewlet):
    """Viewlet interface for CartCheckOutButtonsViewlet"""


class IBillingAndShippingBillingAddressViewlet(IViewlet):
    """Viewlet interface for BillingAndShippingBillingAddressViewlet"""

    def billing_info():
        """Returns dictionary of billing address

        :rtype: dict
        """


class IBillingAndShippingShippingAddressViewlet(IViewlet):
    """Viewlet interface for BillingAndShippingShippingAddressViewlet"""

    def shipping_info():
        """Returns dictionary of shipping address

        :rtype: dict
        """

    def billing_same_as_shipping():
        """Returns True if billing address is same as shipping address

        :rtype: bool
        """


class IBillingAndShippingShippingMethodsViewlet(IViewlet):
    """Viewlet interface for BillingAndShippingShippingMethodsViewlet"""

    def shipping_methods():
        """Returns list of dictionary of shipping methods

        :rtype: list
        """

    def single_shipping_method():
        """Returns True if there is only one shipping method else False

        :rtype: bool
        """


class IBillingAndShippingCheckOutButtonsViewlet(IBaseCheckOutButtonsViewlet):
    """Viewlet interface for BillingAndShippingCheckOutButtonsViewlet"""

    def single_shipping_method():
        """Returns True if there is only one shipping method else False

        :rtype: bool
        """


class IOrderConfirmationCartArticleListingViewlet(ICartArticleListingViewlet):
    """Viewlet interface for OrderConfirmationCartArticleListingViewlet"""


class IOrderConfirmationShippingMethodViewlet(IViewlet):
    """Viewlet interface for OrderConfirmationShippingMethodViewlet"""

    def shipping_method():
        """Returns dictionary of shipping method

        :rtype: dict
        """


class IOrderConfirmationTotalViewlet(IViewlet):
    """Viewlet interface for OrderConfirmationTotalViewlet"""

    def total():
        """Returns localized total money

        :rtype: unicode
        """


class IOrderConfirmationTermsViewlet(IViewlet):
    """Viewlet interface for OrderConfirmationTermsViewlet"""

    def message():
        """Returns dictionary of message

        :rtype: dict
        """


class IOrderConfirmationCheckOutButtonsViewlet(IBaseCheckOutButtonsViewlet):
    """Viewlet interface for OrderConfirmationCheckOutButtonsViewlet"""


class IArticleListingViewlet(IViewlet):
    """Viewlet interface for ArticleListingViewlet"""


class IOrderListingViewlet(IViewlet):
    """Viewlet interface for OrderListingViewlet"""

    def orders():
        """Returns list of dictionary of orders

        :rtype: list
        """

    def class_collapsible():
        """Returns styling values

        :rtype: str
        """


class IOrderListingArticleListingViewlet(IViewlet):
    """Viewlet interface for OrderListingArticleListingViewlet"""


class IOrderListingShippingMethodViewlet(IViewlet):
    """Viewlet interface for OrderListingShippingMethodViewlet"""


class IOrderListingTotalViewlet(IViewlet):
    """Viewlet interface for OrderListingTotalViewlet"""


class IOrderListingAddressesViewlet(IViewlet):
    """Viewlet interface for OrderListingAddressesViewlet"""
