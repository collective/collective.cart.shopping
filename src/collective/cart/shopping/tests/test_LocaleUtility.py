from collective.cart.shopping.interfaces import ILocaleUtility
from collective.cart.shopping.utility.locale import LocaleUtility
from zope.component import getUtility
from zope.component import provideUtility


import unittest


class LocaleUtilityTestCase(unittest.TestCase):
    """TestCase for LocaleUtility"""

    def setUp(self):
        provideUtility(LocaleUtility(), ILocaleUtility)

    def test_instance(self):
        self.assertIsInstance(getUtility(ILocaleUtility), LocaleUtility)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(ILocaleUtility, getUtility(ILocaleUtility)))

    def test___call__(self):
        utility = getUtility(ILocaleUtility)
        self.assertIsNone(utility('AAA'))
        self.assertEqual(utility('fi'), 'fi_FI')
