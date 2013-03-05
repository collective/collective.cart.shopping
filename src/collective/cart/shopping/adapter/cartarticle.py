from collective.cart.core.adapter.cartarticle import CartArticleAdapter as BaseCartArticleAdapter
from collective.cart.shopping.interfaces import ICartArticleAdapter
from five import grok


class CartArticleAdapter(BaseCartArticleAdapter):
    """Adapter for CartArticle."""

    grok.provides(ICartArticleAdapter)

    @property
    def gross_subtotal(self):
        return self.context.gross * self.context.quantity
