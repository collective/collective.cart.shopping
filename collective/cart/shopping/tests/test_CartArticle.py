from collective.cart.shopping.tests.base import IntegrationTestCase
from moneyed import Money
from plone.dexterity.utils import createContentInContainer
from zope.lifecycleevent import modified

import unittest


class ICartArticleTestCase(unittest.TestCase):

    def test_subclass(self):
        from collective.cart import core
        from collective.cart.shopping.interfaces import ICartArticle
        self.assertTrue(issubclass(ICartArticle, core.interfaces.ICartArticle))

    def get_field(self, name):
        """Get field(attribute) based on name.

        :param name: Name of field(attribute).
        :type name: str"""
        from collective.cart.shopping.interfaces import ICartArticle
        return ICartArticle.get(name)

    def test_gross(self):
        self.assertEqual(self.get_field('gross').getDoc(),
            'Gross money of CartArticle')

    def test_net(self):
        self.assertEqual(self.get_field('net').getDoc(),
            'Net money of CartArticle')

    def test_vat(self):
        self.assertEqual(self.get_field('vat').getDoc(),
            'VAT money of CartArticle')

    def test_quantity(self):
        self.assertEqual(self.get_field('quantity').getDoc(),
            'Quantity of CartArticle')

    def test_weight(self):
        self.assertEqual(self.get_field('weight').getDoc(),
            'Weight of CartArticle')

    def test_height(self):
        self.assertEqual(self.get_field('height').getDoc(),
            'Height of CartArticle')

    def test_width(self):
        self.assertEqual(self.get_field('width').getDoc(),
            'Width of CartArticle')

    def test_orig_depth(self):
        self.assertEqual(self.get_field('depth').getDoc(),
            'Depth of CartArticle')


class CartArticleTestSetup(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def create_instance(self):
        instance = createContentInContainer(self.portal, 'collective.cart.core.CartArticle',
            id='1', orig_uuid=u'UUID', checkConstraints=False,
            gross=Money('20.00', currency='EUR'),
            net=Money('15.00', currency='EUR'),
            vat=Money('5.00', currency='EUR'),
            quantity=30,
            weight=100.0,
            height=20.0, width=15.0, depth=10.0)
        modified(instance)
        return instance

    def test_verifyObject(self):
        from collective.cart.shopping.interfaces import ICartArticle
        instance = self.create_instance()
        self.assertTrue(ICartArticle, instance)

    def test_id(self):
        instance = self.create_instance()
        self.assertEqual(instance.id, '1')

    def test_orig_uuid(self):
        instance = self.create_instance()
        self.assertEqual(instance.orig_uuid, u'UUID')

    def test_gross(self):
        instance = self.create_instance()
        self.assertEqual(instance.gross, Money('20.00', currency='EUR'))

    def test_net(self):
        instance = self.create_instance()
        self.assertEqual(instance.net, Money('15.00', currency='EUR'))

    def test_vat(self):
        instance = self.create_instance()
        self.assertEqual(instance.vat, Money('5.00', currency='EUR'))

    def test_quantity(self):
        instance = self.create_instance()
        self.assertEqual(instance.quantity, 30)

    def test_weight(self):
        instance = self.create_instance()
        self.assertEqual(instance.weight, 100.0)

    def test_height(self):
        instance = self.create_instance()
        self.assertEqual(instance.height, 20.0)

    def test_width(self):
        instance = self.create_instance()
        self.assertEqual(instance.width, 15.0)

    def test_depth(self):
        instance = self.create_instance()
        self.assertEqual(instance.depth, 10.0)
