from collective.cart.shopping.interfaces import IMoneyUtility
from collective.cart.shopping.interfaces import IPriceUtility
from decimal import Decimal
from five import grok
from moneyed import Money
from zope.component import getUtility
from zope.interface import implements


class MoneyUtility(grok.GlobalUtility):
    """Utility for Money"""
    implements(IMoneyUtility)

    def __call__(self, money, currency=None, decimal=2):
        price = getUtility(IPriceUtility, name='string')(money.amount, decimal=decimal)
        if currency is None:
            currency = money.currency
        return Money(Decimal(price), currency)
