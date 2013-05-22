from Products.Five.browser import BrowserView
from collective.cart.core.browser.interfaces import ICheckOutView
from collective.cart.shopping.interfaces import IArticle
from plone.memoize.view import memoize
from zExceptions import NotFound


class Miscellaneous(BrowserView):

    @memoize
    def is_article(self):
        return IArticle.providedBy(self.context)

    @memoize
    def is_check_out_view(self):
        view_id = self.context.restrictedTraverse('@@plone_context_state').current_base_url().split('/')[-1]
        try:
            view = self.context.restrictedTraverse(view_id)
            return ICheckOutView.providedBy(view)
        except NotFound:
            return False

