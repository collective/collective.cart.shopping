from collective.cart.core.content import Article as BaseArticle
from collective.cart.core.content import Order as BaseOrder
from collective.cart.core.content import OrderArticle as BaseOrderArticle
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import ICustomerInfo
from collective.cart.shopping.interfaces import IOrder
from collective.cart.shopping.interfaces import IOrderArticle
from collective.cart.shopping.interfaces import IShop
from plone.dexterity.content import Container
from zope.interface import implements


class ArticleContainer(Container):
    """Content type: collective.cart.shopping.ArticleContainer"""
    implements(IArticleContainer)

    _articles_p_mtime = None
    _article_containers_p_mtime = None

    image = None


class Article(BaseArticle):
    """Content type: collective.cart.core.Article"""
    implements(IArticle)

    use_subarticle = False
    image = None
    text = None
    related_articles = []


class Order(BaseOrder):
    """Content type: collective.cart.core.Order"""
    implements(IOrder)

    billing_same_as_shipping = True


class OrderArticle(BaseOrderArticle):
    """Content type: collective.cart.core.OrderArticle"""
    implements(IOrderArticle)

    gross = None
    net = None
    vat = None
    quantity = None


class CustomerInfo(Container):
    """Content type: collective.cart.shopping.CustomerInfo"""
    implements(ICustomerInfo)

    first_name = None
    last_name = None
    organization = None
    vat = None
    email = None
    street = None
    post = None
    city = None
    phone = None
    info_type = None


class Shop(Container):
    """Content type: collective.cart.shopping.Shop"""
    implements(IShop)
