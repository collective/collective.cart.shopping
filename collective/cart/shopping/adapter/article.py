from Products.CMFCore.utils import getToolByName
from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.stock.interfaces import IStock
from collective.behavior.salable.interfaces import ISalable
from collective.cart import core
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from datetime import date
from datetime import datetime
from datetime import time
from five import grok
from plone.memoize.instance import memoize
from zope.lifecycleevent import modified


class ArticleAdapter(core.adapter.article.ArticleAdapter):

    grok.provides(IArticleAdapter)

    @property
    def addable_to_cart(self):
        """True if the Article is addable to cart."""
        return IShoppingSite(self.context).shop and ISalable(
            self.context).salable and not self.context.use_subarticle

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
        modified(carticle)

    @memoize
    def _ulocalized_time(self):
        """Return ulocalized_time method.

        :rtype: method
        """
        translation_service = getToolByName(self.context, 'translation_service')
        return translation_service.ulocalized_time

    @property
    def discount_available(self):
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
    def discount_end(self):
        if self.discount_available:
            if IDiscount(self.context).discount_end:
                ulocalized_time = self._ulocalized_time()
                dt = datetime.combine(IDiscount(self.context).discount_end, time())
                return ulocalized_time(dt, context=self.context)

    @property
    def gross(self):
        if self.discount_available:
            return self.context.discount_gross
        return self.context.gross_money

    @property
    def vat(self):
        if self.discount_available:
            return self.context.discount_vat
        return self.context.vat_money

    @property
    def net(self):
        if self.discount_available:
            return self.context.discount_net
        return self.context.net_money

    @property
    def _quantity_in_carts(self):
        return sum([brain.quantity for brain in self.cart_articles])

    @property
    def soldout(self):
        """Returns True if soldout else False."""
        return not self.addable_to_cart or not IStock(self.context).stock
