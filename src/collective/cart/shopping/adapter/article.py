from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.adapter.article import ArticleAdapter as BaseArticleAdapter
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from datetime import date
from datetime import datetime
from datetime import time
from five import grok
from plone.uuid.interfaces import IUUID


class ArticleAdapter(BaseArticleAdapter):
    """Adapter for Article"""
    grok.context(IArticle)
    grok.provides(IArticleAdapter)

    @property
    def addable_to_cart(self):
        """True if the Article is addable to cart."""
        return super(self.__class__, self).addable_to_cart and not self.context.use_subarticle and not self.articles_in_article

    @property
    def articles_in_article(self):
        """Articles in Article which is not optional subarticle."""
        brains = self.get_brains(IArticle, depth=1, salable=True, sort_on='getObjPositionInParent')
        return not self.context.use_subarticle and brains or []

    @property
    def subarticles(self):
        return self.get_brains(IArticle, depth=1, salable=True, sort_on='getObjPositionInParent', use_subarticle=False)

    @property
    def subarticles_option(self):
        """Subarticles for form select option."""
        subarticles = []
        for brain in self.subarticles:
            obj = brain.getObject()
            if not IArticleAdapter(obj).soldout:
                subarticles.append(obj)
        res = []
        for obj in subarticles:
            article = IArticleAdapter(obj)
            res.append({
                'title': safe_unicode(obj.Title()),
                'gross': article.gross,
                'uuid': IUUID(obj),
            })
        return res

    @property
    def subarticle_addable_to_cart(self):
        """True if the SubArticle is addable to cart."""
        return IShoppingSite(self.context).shop and self.context.use_subarticle

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
        else:
            return 0

    @property
    def quantity_max(self):
        """Maximum quantity which could be added to cart."""
        stock = IStock(self.context).stock
        reducible_quantity = IStock(self.context).reducible_quantity

        if stock > reducible_quantity:
            stock = reducible_quantity

        uuid = IUUID(self.context)
        cart_article = IShoppingSite(self.context).get_cart_article(uuid)
        if cart_article:
            stock -= cart_article['quantity']

        return stock

    def _update_existing_cart_article(self, items, **kwargs):
        """Update cart article which already exists in current cart.
        """
        items['quantity'] += kwargs['quantity']

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
            else:
                return False
        else:
            return False

    @property
    def discount_end(self):
        if self.discount_available:
            if IDiscount(self.context).discount_end:
                dt = datetime.combine(IDiscount(self.context).discount_end, time())
                return self.ulocalized_time(dt, context=self.context)

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
    def soldout(self):
        """Returns True if soldout else False."""
        return not self.addable_to_cart or not IStock(self.context).stock

    @property
    def image_url(self):
        """Returns image url of the article.
        If the image does not exists then returns from parent or fallback image.
        """
        url = '{}/@@images/image'

        if self.context.image:
            return url.format(self.context.absolute_url())

        parent = aq_parent(aq_inner(self.context))
        if IArticle.providedBy(parent):
            if parent.image:
                return url.format(parent.absolute_url())

        portal_url = getToolByName(self.context, 'portal_url')()
        return '{}/fallback.png'.format(portal_url)

    @property
    def title(self):
        """Title is inherited from parent if parent allow subarticles."""
        title = self.context.Title()
        parent = aq_parent(aq_inner(self.context))
        if IArticle.providedBy(parent) and parent.use_subarticle:
            return '{} {}'.format(parent.Title(), title)
        return title
