from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from collective.cart import core
from collective.cart.core.browser.template import CartView
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.stock.interfaces import IStock
from five import grok
from plone.memoize.instance import memoize


grok.templatedir('templates')


class ArticleView(grok.View):
    """Default view for Article."""
    grok.context(IArticle)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('view')
    grok.require('zope2.View')
    grok.template('article')

    def images(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1,
            },
            'object_provides': IATImage.__identifier__,
            'sort_on': 'getObjPositionInParent',
        }
        results = []
        brains = catalog(query)
        if brains:
            for brain in brains:
                results.append({
                    'description': brain.Description,
                    'title': brain.Title,
                    'url': brain.getURL(),
                })
        return results

    def gross(self):
        return IArticleAdapter(self.context).gross

    def discount_end(self):
        return IArticleAdapter(self.context).discount_end

    def image_url(self):
        return IArticleAdapter(self.context).image_url

    def title(self):
        return IArticleAdapter(self.context).title


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


class BaseCheckoutView(grok.View):
    grok.baseclass()
    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.require('zope2.View')

    def update(self):
        if not IShoppingSite(self.context).cart_articles or (
            IShoppingSite(self.context).shipping_methods and not IShoppingSite(self.context).shipping_method):
            url = '{}/@@cart'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        else:
            self.request.set('disable_border', True)
            super(BaseCheckoutView, self).update()


class BillingAndShippingView(BaseCheckoutView):
    grok.name('billing-and-shipping')
    grok.template('billing-and-shipping')


class OrderConfirmationView(BaseCheckoutView):
    grok.name('order-confirmation')
    grok.template('order-confirmation')

    def update(self):
        ids = []
        cart = IShoppingSite(self.context).cart
        if cart is not None:
            ids = cart.objectIds()
        if not 'billing' in ids or not 'shipping' in ids:
            url = '{}/@@cart'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        else:
            super(OrderConfirmationView, self).update()
            self.cart_id = cart.id
            workflow = getToolByName(self.context, 'portal_workflow')
            workflow.doActionFor(cart, 'charge')


class StockListView(grok.View):
    """View to show list of Article stock."""
    grok.context(core.interfaces.IArticle)
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
