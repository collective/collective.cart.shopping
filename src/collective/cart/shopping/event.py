from collective.cart.shopping.interfaces import IArticleAddedToCartEvent
from zope.interface import implements


class ArticleAddedToCartEvent(object):
    implements(IArticleAddedToCartEvent)

    def __init__(self, article, request):
        self.article = article
        self.request = request
