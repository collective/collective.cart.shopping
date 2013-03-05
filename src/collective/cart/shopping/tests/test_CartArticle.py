from collective.cart.shopping.interfaces import ICartArticle
from collective.cart.shopping.tests.base import IntegrationTestCase
from moneyed import Money


class CartArticleTestSetup(IntegrationTestCase):

    def test_subclass(self):
        from collective.cart.core.interfaces import ICartArticle as IBaseCartArticle
        self.assertTrue(issubclass(ICartArticle, IBaseCartArticle))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertTrue(verifyObject(ICartArticle, instance))

    def test_id(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.id, '1')

    def test_gross(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.gross, Money('20.00', currency='EUR'))

    def test_net(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.net, Money('15.00', currency='EUR'))

    def test_vat(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.vat, Money('5.00', currency='EUR'))

    def test_quantity(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.quantity, 30)

    def test_weight(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.weight, 100.0)

    def test_height(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.height, 20.0)

    def test_width(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.width, 15.0)

    def test_depth(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1', gross=self.money('20.00'), net=self.money('15.00'), vat=self.money('5.00'), quantity=30, weight=100.0, height=20.0, width=15.0, depth=10.0)
        self.assertEqual(instance.depth, 10.0)
