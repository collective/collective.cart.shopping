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
        if not self.context.unlimited:
            if self.context.stock < self.context.reducible_quantity:
                return self.context.stock
        return self.context.reducible_quantity

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

    @property
    def _quantity_in_carts(self):
        return sum([brain.quantity for brain in self.cart_articles])

    @property
    def soldout(self):
        """Returns True if soldout else False."""
        if self.addable_to_cart and not IStock(self.context).unlimited:
            return IStock(self.context).stock
