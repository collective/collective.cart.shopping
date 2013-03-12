from collective.cart.shopping.interfaces import IPriceUtility
from decimal import Decimal
from decimal import ROUND_HALF_UP
from five import grok
from zope.interface import implements


class PriceUtility(object):
    """Utility for Price"""
    implements(IPriceUtility)

    def __init__(self, type_in_string):
        self.type = type_in_string

    def __call__(self, price, decimal=2):
        if decimal == 3:
            price = Decimal(str(price)).quantize(Decimal('.0001'), rounding=ROUND_HALF_UP)
            price = Decimal(price).quantize(Decimal('.001'), rounding=ROUND_HALF_UP)
            if self.type == "decimal":
                return price
            if self.type == "string":
                return str(price)
            if self.type == "float":
                return float(price)
        if decimal == 2:
            price = Decimal(str(price)).quantize(Decimal('.001'), rounding=ROUND_HALF_UP)
            price = Decimal(price).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            if self.type == "decimal":
                return price
            if self.type == "string":
                return str(price)
            if self.type == "float":
                return float(price)
        else:
            price = Decimal(str(price)).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
            price = Decimal(price).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
            if self.type == "decimal":
                return price
            if self.type == "string":
                return str(price)
            if self.type == "float":
                return float(price)

grok.global_utility(PriceUtility("float"), IPriceUtility, name="float", direct=True)
grok.global_utility(PriceUtility("decimal"), IPriceUtility, name="decimal", direct=True)
grok.global_utility(PriceUtility("string"), IPriceUtility, name="string", direct=True)
