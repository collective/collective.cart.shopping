from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.adapter.article import ArticleAdapter as BaseArticleAdapter
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IMoneyUtility
from collective.cart.shopping.interfaces import IShoppingSite
from datetime import date
from datetime import datetime
from datetime import time
from plone.uuid.interfaces import IUUID
from zope.component import adapts
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

PMF = MessageFactory("plone")


class ArticleAdapter(BaseArticleAdapter):
    """Adapter for content type: collective.cart.core.Article"""
    adapts(IArticle)
    implements(IArticleAdapter)

    def articles(self, salable=None, use_subarticle=None):
        """Returns brain of articles located directly under context"""
        query = {}
        if salable is not None:
            query['salable'] = salable
        if use_subarticle is not None:
            query['use_subarticle'] = use_subarticle
        return self.get_brains(IArticle, depth=1, sort_on='getObjPositionInParent', **query)

    def soldout(self):
        """Returns True if soldout else False."""
        if self.context.use_subarticle:
            stocks = [IStock(subarticle.getObject()).stock() for subarticle in self.articles(salable=True, use_subarticle=False)]
            if sum(stocks):
                return False
            else:
                return True

        return self.context.salable and not IStock(self.context).stock()

    def subarticles(self):
        """Returns subarticles for form select option

        :rtype: list
        """
        res = []
        if self.context.use_subarticle:
            subarticles = []
            shopping_site = IShoppingSite(self.context)
            for brain in self.articles(salable=True, use_subarticle=False):
                obj = brain.getObject()
                if not IArticleAdapter(obj).soldout():
                    subarticles.append(obj)
            wftool = getToolByName(self.context, 'portal_workflow')
            wf = wftool.getChainFor(self.context)[0]
            for obj in subarticles:

                state = wftool.getStatusOf(wf, obj)['review_state']
                if state != 'private':
                    state = ''
                res.append({
                    'title': safe_unicode(obj.Title()),
                    'gross': shopping_site.format_money(IArticleAdapter(obj).gross()),
                    'uuid': IUUID(obj),
                    'state': PMF(state),
                })
        return res

    def quantity_max(self):
        """Maximum quantity which could be added to cart."""
        obj = self.context

        if self.context.use_subarticle:
            articles = self.articles(salable=True, use_subarticle=False)
            if articles:
                obj = articles[0].getObject()

        stock = IStock(obj).stock()
        reducible_quantity = IStock(obj).reducible_quantity

        if stock > reducible_quantity:
            stock = reducible_quantity

        uuid = IUUID(obj)
        article = IShoppingSite(self.context).get_cart_article(uuid)
        if article:
            stock -= article['quantity']

        return stock

    def _update_existing_cart_article(self, items, **kwargs):
        """Update cart article which already exists in current cart.
        """
        items['quantity'] += kwargs['quantity']

    def discount_available(self):
        """Returns True if discount is available else False

        :rtype: bool
        """
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

    def discount_end(self):
        """Returns localized date for discount end"""
        if self.discount_available():
            discount = IDiscount(self.context)
            if discount.discount_end:
                dt = datetime.combine(discount.discount_end, time())
                return self.context.restrictedTraverse('@@plone').toLocalizedTime(dt)

    def gross(self):
        """Returns gross money

        :rtype: moneyed.Money
        """
        if self.discount_available():
            return self.context.discount_money
        # return self.context.money
        return IDiscount(self.context).money

    def get_net(self, gross):
        rate = self.context.vat_rate
        return getUtility(IMoneyUtility)(gross * (1.0 - rate / (100 + rate)))

    def get_vat(self, gross):
        rate = self.context.vat_rate
        return getUtility(IMoneyUtility)(gross * rate / (100 + rate))

    def image_url(self, size=None):
        """Return image url of the article.
        If the image does not exists then returns from parent or fallback image.

        :param size: Size of image such as preview and mini.
        :type size: string

        :rtype: string
        """
        url = '{}/@@images/image'
        if size:
            url = '{}/{}'.format(url, size)

        if self.context.image:
            return url.format(self.context.absolute_url())

        parent = aq_parent(aq_inner(self.context))
        if IArticle.providedBy(parent):
            if parent.image:
                return url.format(parent.absolute_url())

        portal_url = getToolByName(self.context, 'portal_url')()
        return '{}/fallback.png'.format(portal_url)

    def title(self):
        """Title is inherited from parent if parent allow subarticles."""
        title = self.context.Title()
        parent = aq_parent(aq_inner(self.context))
        if IArticle.providedBy(parent):
            title = '{} {}'.format(parent.Title(), title)
            parent = aq_parent(parent)
            if IArticle.providedBy(parent):
                return '{} {}'.format(parent.Title(), title)
        return title
