from collective.base.adapter import Adapter
from collective.cart.shopping.interfaces import IOrderArticle
from collective.cart.shopping.interfaces import IOrderArticleAdapter
from zope.component import adapts
from zope.interface import implements


class OrderArticleAdapter(Adapter):
    """Adapter for content type: collective.cart.core.OrderArticle"""

    adapts(IOrderArticle)
    implements(IOrderArticleAdapter)

    def gross_subtotal(self):
        """Returns subtotal"""
        return self.context.gross * self.context.quantity
