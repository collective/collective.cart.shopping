from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from collective.cart.core.browser.template import CartContentView
from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IArticleAdapter
from five import grok
from zope.component import getMultiAdapter

grok.templatedir('templates')


class ArticleView(grok.View):

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


class CartContentView(CartContentView):
    grok.layer(ICollectiveCartShoppingLayer)

    def billing(self):
        return self.context.get('billing')

    def shipping(self):
        return self.context.get('shipping')


class BillingAndShippingView(grok.View):

    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('billing-and-shipping')
    grok.require('zope2.View')
    grok.template('billing-and-shipping')

    def __call__(self):
        if not IShoppingSite(self.context).cart_articles:
            url = '{}/@@cart'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        else:
            return super(BillingAndShippingView, self).__call__()
