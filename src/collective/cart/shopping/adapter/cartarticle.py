from collective.cart.core.adapter.cartarticle import CartArticleAdapter as BaseCartArticleAdapter
from collective.cart.shopping.interfaces import ICartArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from five import grok


class CartArticleAdapter(BaseCartArticleAdapter):
    """Adapter for CartArticle."""

    grok.provides(ICartArticleAdapter)

    @property
    def gross_subtotal(self):
        """Returns subtotal"""
        return self.context.gross * self.context.quantity

    def locale_gross_subtotal(self):
        """Returns localized subtotal"""
        return IShoppingSite(self.context).format_money(self.gross_subtotal)
