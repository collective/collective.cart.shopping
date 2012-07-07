from collective.cart.core.interfaces import IArticle
from five import grok
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer


grok.templatedir('templates')


class ArticleView(grok.View):

    grok.context(IArticle)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.name('view')
    grok.require('zope2.View')
    grok.template('article')


# class CartView(grok.View):

#     grok.context(IShoppingSiteRoot)
#     grok.layer(ICollectiveCartShoppingLayer)
#     grok.name('view')
#     grok.require('zope2.View')
#     grok.template('cart')
