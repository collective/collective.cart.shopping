from collective.cart import core
from collective.cart.shopping.interfaces import ICartArticleAdapter
from five import grok


class CartArticleAdapter(core.adapter.cartarticle.CartArticleAdapter):
    """Adapter to handle CartArticle."""

    grok.provides(ICartArticleAdapter)

    @property
    def gross_subtotal(self):
        return self.context.gross * self.context.quantity
