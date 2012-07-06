from collective.behavior.discount.interfaces import IDiscount
from collective.cart.core.adapter.article import ArticleAdapter
from collective.cart.shopping.interfaces import IArticleAdapter
from datetime import date
from five import grok


class ArticleAdapter(ArticleAdapter):

    grok.provides(IArticleAdapter)

    @property
    def _discount_available(self):
        discount = IDiscount(self.context)
        if discount.discount_enabled:
            today = date.today()
            return today > discount.discount_start and today < discount.discount_end

    @property
    def gross(self):
        if self._discount_available:
            return self.context.discount_gross
        return self.context.gross_money

    @property
    def vat(self):
        if self._discount_available:
            return self.context.discount_vat
        return self.context.vat_money

    @property
    def net(self):
        if self._discount_available:
            return self.context.discount_net
        return self.context.net_money
