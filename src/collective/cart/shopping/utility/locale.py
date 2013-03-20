from collective.cart.shopping.config import LOCALES
from collective.cart.shopping.interfaces import ILocaleUtility
from five import grok
from plone.memoize.instance import memoize
from zope.interface import implements


class LocaleUtility(grok.GlobalUtility):
    """Utility for Locale"""
    implements(ILocaleUtility)

    @memoize
    def __call__(self, code):
        """Returns combined language code from single code.

        :param code: Single lower case language code
        :type code: str

        :rtype: str or None
        """
        return dict(LOCALES).get(code)
