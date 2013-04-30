# -*- coding: utf-8 -*-
from collective.cart.shopping.interfaces import IUnicodeUtility
from collective.cart.shopping.utility.unicode import UnicodeUtility
from zope.component import getUtility

import unittest


class UnicodeUtilityTestCase(unittest.TestCase):
    """TestCase for UnicodeUtility"""

    def setUp(self):
        from zope.component import provideUtility
        provideUtility(UnicodeUtility(), IUnicodeUtility)

    def test_subclass(self):
        from zope.interface import Interface
        self.assertTrue(issubclass(IUnicodeUtility, Interface))
        self.assertTrue(issubclass(UnicodeUtility, object))

    def test_instance(self):
        self.assertIsInstance(getUtility(IUnicodeUtility), UnicodeUtility)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(IUnicodeUtility, getUtility(IUnicodeUtility)))

    def test_safe_unicode(self):
        utility = getUtility(IUnicodeUtility)
        self.assertEqual(utility.safe_unicode('AAA'), u'AAA')
        self.assertIsInstance(utility.safe_unicode('AAA'), unicode)

        self.assertEqual(utility.safe_unicode('ÄÄÄ', 'utf-8'), u'ÄÄÄ')
        self.assertIsInstance(utility.safe_unicode('ÄÄÄ', 'utf-8'), unicode)

    def test_address(self):
        utility = getUtility(IUnicodeUtility)
        address = {}
        with self.assertRaises(KeyError):
            utility.address(address)

        address['first_name'] = 'FIRST'
        with self.assertRaises(KeyError):
            utility.address(address)

        address['last_name'] = 'LAST'
        with self.assertRaises(KeyError):
            utility.address(address)

        address['organization'] = ''
        with self.assertRaises(KeyError):
            utility.address(address)

        address['vat'] = ''
        with self.assertRaises(KeyError):
            utility.address(address)

        address['street'] = 'STREET'
        with self.assertRaises(KeyError):
            utility.address(address)

        address['post'] = 'POST'
        with self.assertRaises(KeyError):
            utility.address(address)

        address['city'] = 'CITY'
        with self.assertRaises(KeyError):
            utility.address(address)

        address['phone'] = 'PHONE'
        with self.assertRaises(KeyError):
            utility.address(address)

        address['email'] = 'EMAIL'
        self.assertEqual(utility.address(address), u'FIRST LAST    \nSTREET\nPOST CITY\nPHONE\nEMAIL\n')
        self.assertIsInstance(utility.address(address), unicode)
