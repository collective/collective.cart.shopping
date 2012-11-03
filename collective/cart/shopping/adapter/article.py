from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.salable.interfaces import ISalable
from collective.behavior.stock.interfaces import IStock
from collective.cart import core
from collective.cart.shopping import _
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from datetime import date
from datetime import datetime
from datetime import time
from five import grok
from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
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
            'sort_on': 'getObjPositionInParent',
        })
        return brains

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
        else:
            return 0

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

    @property
    def image_url(self):
        """Returns image url of the article.
        If the image does not exists then return from parent or fallback image.
        """
        url = '{}/@@images/image'

        if self.context.image:
            return url.format(self.context.absolute_url())

        parent = aq_parent(aq_inner(self.context))
        if IArticle.providedBy(parent):
            if parent.image:
                return url.format(parent.absolute_url())

        portal_url = getToolByName(self.context, 'portal_url')()
        return '{}/++theme++slt.theme/images/fallback.png'.format(portal_url)

    @property
    def title(self):
        """Title is inherited from parent if parent allow subarticles."""
        title = self.context.Title()
        parent = aq_parent(aq_inner(self.context))
        if IArticle.providedBy(parent) and parent.use_subarticle:
            return '{} {}'.format(parent.Title(), title)
        return title