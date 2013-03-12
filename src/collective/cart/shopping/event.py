from collective.cart.shopping.interfaces import IArticleAddedToCartEvent
from collective.cart.shopping.interfaces import IBillingAddressConfirmedEvent
from collective.cart.shopping.interfaces import IShippingAddressConfirmedEvent
from zope.interface import implements


class ArticleAddedToCartEvent(object):
    implements(IArticleAddedToCartEvent)

    def __init__(self, article, request):
        self.article = article
        self.request = request


class BillingAddressConfirmedEvent(object):
    implements(IBillingAddressConfirmedEvent)

    def __init__(self, context):
        self.context = context


class ShippingAddressConfirmedEvent(object):
    implements(IShippingAddressConfirmedEvent)

    def __init__(self, context):
        self.context = context
