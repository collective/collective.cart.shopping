from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.salable.interfaces import ISalable
from collective.behavior.stock.interfaces import IStock
from collective.cart import core
from collective.cart.shopping import _
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
        context = aq_inner(self.context)
        return IShoppingSite(context).shop and ISalable(
                context).salable and not context.use_subarticle and not self.subarticles

    @property
    def subarticles(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog({
            'object_provides': core.interfaces.IArticle.__identifier__,
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'depth': 1,
            },
            'salable': True,
        })
        return brains

    @property
    def subarticles_option(self):
        """Subarticles for form select option."""
        res = []
        for brain in self.subarticles:
            obj = brain.getObject()
            article = IArticleAdapter(obj)
            base_text = u'${title}  ${gross} ${currency}  VAT ${vat_rate} %'
            base_mapping = {
                'title': safe_unicode(brain.Title),
                'gross': article.gross.amount,
                'currency': article.gross.currency,
                'vat_rate': brain.vat,
            }
            option = _(u'subarticle_option', base_text, mapping=base_mapping)
            discount_text = base_text + u'  Discount valid till ${discount_end}  Normal Price: ${money} ${currency}'
            discount_mapping = base_mapping.copy()
            discount_mapping['discount_end'] = article.discount_end
            discount_mapping['money'] = brain.money.amount
            discount_option = _(u'subarticle_option_discount', discount_text, mapping=discount_mapping)
            if article.discount_available:
                option = discount_option
            res.append({
                'option': option,
                'uuid': brain.UID,
            })
        return res

    @property
    def articles_in_article(self):
        """Articles in Article which is not optional subarticle."""
        return not self.context.use_subarticle and self.subarticles or []

    @property
    def subarticle_addable_to_cart(self):
        """True if the SubArticle is addable to cart."""
        return IShoppingSite(
            self.context).shop and self.context.use_subarticle

    @property
    def subarticle_soldout(self):
        """True or False for subarticle sold out."""
        if self.subarticles:
            stocks = [
                IStock(subarticle.getObject()).stock for subarticle in self.subarticles]
            if sum(stocks):
                return False
        return True

    @property
    def subarticle_quantity_max(self):
        """Minimum max quantity for all the subarticles."""
        quantities = [
            IArticleAdapter(subarticle.getObject()).quantity_max for subarticle in self.subarticles]
        if quantities:
            return min(quantities)

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
