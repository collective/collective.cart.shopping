from Products.statusmessages.interfaces import IStatusMessage
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.browser.viewlet import AddToCartViewlet
from collective.cart.core.browser.viewlet import CartArticlesViewlet
from collective.cart.core.interfaces import ICartArticleAdapter
from collective.cart.shopping import _
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IArticleAdapter
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from zope.lifecycleevent import modified


grok.templatedir('viewlets')


class AddToCartViewlet(AddToCartViewlet):
    """Viewlet to show add to cart form for salable article.

    Can also add with certain number of quantity.
    """
    grok.layer(ICollectiveCartShoppingLayer)

    def update(self):
        form = self.request.form
        if form.get('form.addtocart', None) is not None:
            quantity = form.get('quantity', None)
            if quantity is not None:
                try:
                    quantity = int(quantity)
                    item = IArticleAdapter(self.context)
                    kwargs = {
                        'gross': item.gross,
                        'net': item.net,
                        'vat': item.vat,
                        'quantity': quantity,
                    }
                    IArticleAdapter(self.context).add_to_cart(**kwargs)
                    if not self.context.unlimited:
                        IStock(self.context).stock -= quantity
                        modified(self.context)
                    return self.render()
                except ValueError:
                    message = _(u"Input integer value to add to cart.")
                    IStatusMessage(self.request).addStatusMessage(message, type='warn')
                    return self.render()

    @property
    def quantity_max(self):
        """Max quantity."""
        return IArticleAdapter(self.context).quantity_max

    def quantity_size(self):
        """Size for quantity field."""
        return len(str(self.quantity_max))

    def numbers(self):
        """Iterable all numbers."""
        return xrange(1, self.quantity_max + 1)


class CartArticlesViewlet(CartArticlesViewlet):
    """Cart Articles Viewlet Class."""
    grok.layer(ICollectiveCartShoppingLayer)

    @property
    def articles(self):
        """Returns list of articles to show in cart."""
        results = []
        for item in IContentListing(self.view.cart_articles):
            obj = item.getObject()
            items = self._items(item)
            items['orig'] = None
            items['gross'] = obj.gross
            items['quantity'] = obj.quantity
            orig_article = ICartArticleAdapter(obj).orig_article
            if orig_article:
                items['orig'] = orig_article
            results.append(items)
        return results
