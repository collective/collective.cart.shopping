from collective.cart.shopping.content import OrderArticle
from collective.cart.shopping.interfaces import IOrderArticle

import unittest


class OrderArticleTestCase(unittest.TestCase):
    """TestCase for OrderArticle"""

    def test_subclass(self):
        from collective.cart.core.interfaces import IOrderArticle as IBaseOrderArticle
        self.assertTrue(issubclass(IOrderArticle, IBaseOrderArticle))
        from collective.cart.core.content import OrderArticle as BaseOrderArticle
        self.assertTrue(issubclass(OrderArticle, BaseOrderArticle))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(IOrderArticle, OrderArticle()))

    def test_gross(self):
        instance = OrderArticle()
        self.assertIsNone(instance.gross)

    def test_net(self):
        instance = OrderArticle()
        self.assertIsNone(instance.net)

    def test_vat(self):
        instance = OrderArticle()
        self.assertIsNone(instance.vat)

    def test_quantity(self):
        instance = OrderArticle()
        self.assertIsNone(instance.quantity)
