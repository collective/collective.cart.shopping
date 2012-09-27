from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from collective.cart.core.browser.template import CartView
from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.stock.interfaces import IStock
from five import grok
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter


grok.templatedir('templates')


class ArticleView(grok.View):
    """Default view for Article."""
    grok.context(IArticle)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('view')
    grok.require('zope2.View')
    grok.template('article')

    def image(self):
        scales = getMultiAdapter((self.context, self.request), name='images')
        scale = scales.scale('image', scale='preview')
        if scale:
            return scale.tag()

    def images(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1,
            },
            'object_provides': IATImage.__identifier__,
        }
        results = []
        brains = catalog(query)
        if brains:
            for brain in catalog(query):
                obj = brain.getObject()
                scales = getMultiAdapter((obj, self.request), name='images')
                scale = scales.scale('image', scale='thumb')
                results.append(scale.tag())
        return results

    def gross(self):
        return IArticleAdapter(self.context).gross

    def discount_end(self):
        return IArticleAdapter(self.context).discount_end


class ArticleContainerView(grok.View):
    """Default view for ArticleContainer."""
    grok.context(IArticleContainer)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('view')
    grok.require('zope2.View')
    grok.template('article-container')


class ShoppingCartView(CartView):
    """Cart View"""
    grok.layer(ICollectiveCartShoppingLayer)


class BillingAndShippingView(grok.View):

    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('billing-and-shipping')
    grok.require('zope2.View')
    grok.template('billing-and-shipping')

    def update(self):
        if not IShoppingSite(self.context).cart_articles:
            url = '{}/@@cart'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        else:
            self.request.set('disable_border', True)
            super(BillingAndShippingView, self).update()


class OrderConfirmationView(grok.View):

    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('order-confirmation')
    grok.require('zope2.View')
    grok.template('order-confirmation')

    def update(self):
        base_url = self.context.absolute_url()
        if not IShoppingSite(self.context).cart_articles:
            url = '{}/@@cart'.format(base_url)
            return self.request.response.redirect(url)
        else:
            self.request.set('disable_border', True)
            super(OrderConfirmationView, self).update()


class StockListView(grok.View):
    """View to show list of Article stock."""
    grok.context(IArticle)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('stock-list')
    grok.require('cmf.ModifyPortalContent')
    grok.template('stock-list')

    def stocks(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1,
            },
            'object_provides': IStock.__identifier__,
            'sort_on': 'created',
            'sort_order': 'descending',
        }
        res = []
        for brain in catalog(query):
            items = {
                'url': brain.getURL(),
                'title': brain.Title,
                'description': brain.Description,
                'crated': self._date(brain.created),
                'initial_stock': brain.initial_stock,
                'current_stock': brain.stock,
                'money': brain.money,
            }
            res.append(items)
        return res

    @memoize
    def _ulocalized_time(self):
        """Return ulocalized_time method.

        :rtype: method
        """
        translation_service = getToolByName(self.context, 'translation_service')
        return translation_service.ulocalized_time

    def _date(self, date):
        """Returns localized date.

        :param date: Date and time.
        :type date: DateTime.DateTime
        """
        ulocalized_time = self._ulocalized_time()
        return ulocalized_time(date, context=self.context)
