from Products.Five.browser import BrowserView
from collective.cart.shopping.interfaces import IArticle
from plone.memoize.view import memoize


class Miscellaneous(BrowserView):

    @memoize
    def is_article(self):
        return IArticle.providedBy(self.context)
