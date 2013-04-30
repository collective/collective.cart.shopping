from collective.cart.shopping.interfaces import IPriceUtility
from collective.cart.shopping.utility.price import PriceUtility
from decimal import Decimal
from zope.component import getUtility

import unittest


class PriceUtilityTestCase(unittest.TestCase):
    """TestCase for PriceUtility"""

    def setUp(self):
        from zope.component import provideUtility
        provideUtility(PriceUtility('float'), IPriceUtility, name=u'float')
        provideUtility(PriceUtility('decimal'), IPriceUtility, name=u'decimal')
        provideUtility(PriceUtility('string'), IPriceUtility, name=u'string')

    def test_subclass(self):
        from zope.interface import Interface
        self.assertTrue(issubclass(IPriceUtility, Interface))
        self.assertTrue(issubclass(PriceUtility, object))

    def test_instance(self):
        self.assertIsInstance(getUtility(IPriceUtility, name="float"), PriceUtility)
        self.assertIsInstance(getUtility(IPriceUtility, name="decimal"), PriceUtility)
        self.assertIsInstance(getUtility(IPriceUtility, name="string"), PriceUtility)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(IPriceUtility, getUtility(IPriceUtility, name="float")))
        self.assertTrue(verifyObject(IPriceUtility, getUtility(IPriceUtility, name="decimal")))
        self.assertTrue(verifyObject(IPriceUtility, getUtility(IPriceUtility, name="string")))

    def test___call__(self):
        float_utility = getUtility(IPriceUtility, name="float")
        decimal_utility = getUtility(IPriceUtility, name="decimal")
        string_utility = getUtility(IPriceUtility, name="string")

        price = 0
        self.assertEqual(float_utility(price), 0.0)
        self.assertEqual(decimal_utility(price), Decimal('0.00'))
        self.assertEqual(string_utility(price), '0.00')
        self.assertEqual(float_utility(price, 3), 0.0)
        self.assertEqual(decimal_utility(price, 3), Decimal('0.000'))
        self.assertEqual(string_utility(price, 3), '0.000')
        self.assertEqual(float_utility(price, 1), 0.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('0'))
        self.assertEqual(string_utility(price, 1), '0')
        self.assertEqual(float_utility(price, 0), 0.0)
        self.assertEqual(decimal_utility(price, 0), Decimal('0'))
        self.assertEqual(string_utility(price, 0), '0')
        self.assertEqual(float_utility(price, -1), 0.0)
        self.assertEqual(decimal_utility(price, -1), Decimal('0'))
        self.assertEqual(string_utility(price, -1), '0')
        self.assertEqual(float_utility(price, 'A'), 0.0)
        self.assertEqual(decimal_utility(price, 'A'), Decimal('0'))
        self.assertEqual(string_utility(price, 'A'), '0')

        price = 1
        self.assertEqual(float_utility(price), 1.0)
        self.assertEqual(decimal_utility(price), Decimal('1.00'))
        self.assertEqual(string_utility(price), '1.00')
        self.assertEqual(float_utility(price, 3), 1.0)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.000'))
        self.assertEqual(string_utility(price, 3), '1.000')
        self.assertEqual(float_utility(price, 1), 1.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('1'))
        self.assertEqual(string_utility(price, 1), '1')

        price = 1.9
        self.assertEqual(float_utility(price), 1.9)
        self.assertEqual(decimal_utility(price), Decimal('1.90'))
        self.assertEqual(string_utility(price), '1.90')
        self.assertEqual(float_utility(price, 3), 1.9)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.900'))
        self.assertEqual(string_utility(price, 3), '1.900')
        self.assertEqual(float_utility(price, 1), 2.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('2'))
        self.assertEqual(string_utility(price, 1), '2')

        price = 1.4
        self.assertEqual(float_utility(price), 1.4)
        self.assertEqual(decimal_utility(price), Decimal('1.40'))
        self.assertEqual(string_utility(price), '1.40')
        self.assertEqual(float_utility(price, 3), 1.4)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.400'))
        self.assertEqual(string_utility(price, 3), '1.400')
        self.assertEqual(float_utility(price, 1), 1.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('1'))
        self.assertEqual(string_utility(price, 1), '1')

        price = 1.45
        self.assertEqual(float_utility(price), 1.45)
        self.assertEqual(decimal_utility(price), Decimal('1.45'))
        self.assertEqual(string_utility(price), '1.45')
        self.assertEqual(float_utility(price, 3), 1.45)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.450'))
        self.assertEqual(string_utility(price, 3), '1.450')
        self.assertEqual(float_utility(price, 1), 2.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('2'))
        self.assertEqual(string_utility(price, 1), '2')

        price = 1.44
        self.assertEqual(float_utility(price), 1.44)
        self.assertEqual(decimal_utility(price), Decimal('1.44'))
        self.assertEqual(string_utility(price), '1.44')
        self.assertEqual(float_utility(price, 3), 1.44)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.440'))
        self.assertEqual(string_utility(price, 3), '1.440')
        self.assertEqual(float_utility(price, 1), 1.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('1'))
        self.assertEqual(string_utility(price, 1), '1')

        price = 1.445
        self.assertEqual(float_utility(price), 1.45)
        self.assertEqual(decimal_utility(price), Decimal('1.45'))
        self.assertEqual(string_utility(price), '1.45')
        self.assertEqual(float_utility(price, 3), 1.445)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.445'))
        self.assertEqual(string_utility(price, 3), '1.445')
        self.assertEqual(float_utility(price, 1), 1.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('1'))
        self.assertEqual(string_utility(price, 1), '1')

        price = '1.445'
        self.assertEqual(float_utility(price), 1.45)
        self.assertEqual(decimal_utility(price), Decimal('1.45'))
        self.assertEqual(string_utility(price), '1.45')
        self.assertEqual(float_utility(price, 3), 1.445)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.445'))
        self.assertEqual(string_utility(price, 3), '1.445')
        self.assertEqual(float_utility(price, 1), 1.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('1'))
        self.assertEqual(string_utility(price, 1), '1')

        price = Decimal('1.445')
        self.assertEqual(float_utility(price), 1.45)
        self.assertEqual(decimal_utility(price), Decimal('1.45'))
        self.assertEqual(string_utility(price), '1.45')
        self.assertEqual(float_utility(price, 3), 1.445)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.445'))
        self.assertEqual(string_utility(price, 3), '1.445')
        self.assertEqual(float_utility(price, 1), 1.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('1'))
        self.assertEqual(string_utility(price, 1), '1')

        price = Decimal(1.445)
        self.assertEqual(float_utility(price), 1.45)
        self.assertEqual(decimal_utility(price), Decimal('1.45'))
        self.assertEqual(string_utility(price), '1.45')
        self.assertEqual(float_utility(price, 3), 1.445)
        self.assertEqual(decimal_utility(price, 3), Decimal('1.445'))
        self.assertEqual(string_utility(price, 3), '1.445')
        self.assertEqual(float_utility(price, 1), 1.0)
        self.assertEqual(decimal_utility(price, 1), Decimal('1'))
        self.assertEqual(string_utility(price, 1), '1')
