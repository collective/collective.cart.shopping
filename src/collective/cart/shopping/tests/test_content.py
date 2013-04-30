from collective.cart.shopping.content import Article
from collective.cart.shopping.content import ArticleContainer
from collective.cart.shopping.content import CustomerInfo
from collective.cart.shopping.content import Order
from collective.cart.shopping.content import OrderArticle
from collective.cart.shopping.content import Shop
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import ICustomerInfo
from collective.cart.shopping.interfaces import IOrder
from collective.cart.shopping.interfaces import IOrderArticle
from collective.cart.shopping.interfaces import IShop
from plone.dexterity.content import Container
from plone.supermodel.model import Schema
from zope.interface.verify import verifyObject

import unittest


class ArticleContainerTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.shopping.ArticleContainer"""

    def test_subclass(self):
        from collective.cart.shopping.schema import ArticleContainerSchema
        self.assertTrue(issubclass(ArticleContainer, Container))
        self.assertTrue(issubclass(ArticleContainerSchema, Schema))
        self.assertTrue(issubclass(IArticleContainer, (ArticleContainerSchema)))

    def test_verifyObject(self):
        self.assertTrue(verifyObject(IArticleContainer, ArticleContainer()))


class ArticleTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.core.Article"""

    def test_subclass(self):
        from collective.cart.core.content import Article as BaseArticle
        from collective.cart.core.interfaces import IArticle as IBaseArticle
        from collective.cart.core.schema import ArticleSchema as BaseArticleSchema
        from collective.cart.shopping.schema import ArticleSchema
        self.assertTrue(issubclass(Article, BaseArticle))
        self.assertTrue(issubclass(ArticleSchema, BaseArticleSchema))
        self.assertTrue(issubclass(IArticle, (ArticleSchema, IBaseArticle)))

    def test_verifyObject(self):
        self.assertTrue(verifyObject(IArticle, Article()))

    def test_user_subarticle(self):
        self.assertFalse(Article().use_subarticle)

    def test_image(self):
        self.assertIsNone(Article().image)

    def test_text(self):
        self.assertIsNone(Article().text)


class OrderTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.core.Order"""

    def test_subclass(self):
        from collective.cart.core.content import Order as BaseOrder
        from collective.cart.core.interfaces import IOrder as IBaseOrder
        from collective.cart.core.schema import OrderSchema as BaseOrderSchema
        from collective.cart.shopping.schema import OrderSchema
        self.assertTrue(issubclass(Order, BaseOrder))
        self.assertTrue(issubclass(OrderSchema, BaseOrderSchema))
        self.assertTrue(issubclass(IOrder, (OrderSchema, IBaseOrder)))

    def test_verifyObject(self):
        self.assertTrue(verifyObject(IOrder, Order()))

    def test_billing_same_as_shipping(self):
        self.assertTrue(Order().billing_same_as_shipping)


class OrderArticleTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.core.OrderArticle"""

    def test_subclass(self):
        from collective.cart.core.content import OrderArticle as BaseOrderArticle
        from collective.cart.core.interfaces import IOrderArticle as IBaseOrderArticle
        from collective.cart.core.schema import OrderArticleSchema as BaseOrderArticleSchema
        from collective.cart.shopping.schema import OrderArticleSchema
        self.assertTrue(issubclass(OrderArticle, BaseOrderArticle))
        self.assertTrue(issubclass(OrderArticleSchema, BaseOrderArticleSchema))
        self.assertTrue(issubclass(IOrderArticle, (OrderArticleSchema, IBaseOrderArticle)))

    def test_verifyObject(self):
        self.assertTrue(verifyObject(IOrderArticle, OrderArticle()))

    def test_gross(self):
        self.assertIsNone(OrderArticle().gross)

    def test_net(self):
        self.assertIsNone(OrderArticle().net)

    def test_vat(self):
        self.assertIsNone(OrderArticle().vat)

    def test_quantity(self):
        self.assertIsNone(OrderArticle().quantity)


class CustomerInfoTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.shopping.CustomerInfo"""

    def test_subclass(self):
        from collective.cart.shopping.schema import CustomerInfoSchema
        self.assertTrue(issubclass(CustomerInfo, Container))
        self.assertTrue(issubclass(CustomerInfoSchema, Schema))
        self.assertTrue(issubclass(ICustomerInfo, (CustomerInfoSchema)))

    def test_verifyObject(self):
        self.assertTrue(verifyObject(ICustomerInfo, CustomerInfo()))

    def test_first_name(self):
        self.assertIsNone(CustomerInfo().first_name)

    def test_last_name(self):
        self.assertIsNone(CustomerInfo().last_name)

    def test_organization(self):
        self.assertIsNone(CustomerInfo().organization)

    def test_vat(self):
        self.assertIsNone(CustomerInfo().vat)

    def test_email(self):
        self.assertIsNone(CustomerInfo().email)

    def test_street(self):
        self.assertIsNone(CustomerInfo().street)

    def test_post(self):
        self.assertIsNone(CustomerInfo().post)

    def test_city(self):
        self.assertIsNone(CustomerInfo().city)

    def test_phone(self):
        self.assertIsNone(CustomerInfo().phone)

    def test_info_type(self):
        self.assertIsNone(CustomerInfo().info_type)


class ShopTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.shopping.Shop"""

    def test_subclass(self):
        from collective.cart.core.interfaces import IShoppingSiteRoot
        from collective.cart.shopping.schema import ShopSchema
        self.assertTrue(issubclass(Shop, Container))
        self.assertTrue(issubclass(ShopSchema, Schema))
        self.assertTrue(issubclass(IShop, (ShopSchema, IShoppingSiteRoot)))

    def test_verifyObject(self):
        self.assertTrue(verifyObject(IShop, Shop()))
