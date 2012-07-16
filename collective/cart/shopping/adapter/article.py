from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.adapter.article import ArticleAdapter
from collective.cart.shopping.interfaces import IArticleAdapter
from datetime import date
from five import grok


class ArticleAdapter(ArticleAdapter):

    grok.provides(IArticleAdapter)

    @property
    def quantity_max(self):
        """Max quantity which could be added to cart."""
        if IStock(self.context).stock < IStock(self.context).reducible_quantity:
            return IStock(self.context).stock
        return IStock(self.context).reducible_quantity

    def _update_existing_cart_article(self, carticle, **kwargs):
        """Update cart article which already exists in current cart.

        :param carticle: Cart Article.
        :type carticle: collective.cart.core.CartArticle
        """
        carticle.quantity += kwargs['quantity']

    @property
    def _discount_available(self):
        discount = IDiscount(self.context)
        if discount.discount_enabled:
            today = date.today()
            start = discount.discount_start
            end = discount.discount_end
            if start and end:
                return today >= start and today <= end
            elif start:
                return today >= start
            elif end:
                return today <= end

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

    @property
    def _quantity_in_carts(self):
        return sum([brain.quantity for brain in self.cart_articles])

    @property
    def soldout(self):
        """Returns True if soldout else False."""
        return not self.addable_to_cart or not IStock(self.context).stock
