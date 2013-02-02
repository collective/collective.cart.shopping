from Products.Five.browser import BrowserView
from collective.cart.shopping.interfaces import IArticle


class Miscellaneous(BrowserView):

    def is_article(self):
        return IArticle.providedBy(self.context)
