from Acquisition import aq_inner
from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from collective.cart import core
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping import _
from collective.cart.shopping.browser.base import Message
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICustomerInfo
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.stock.interfaces import IStock
from five import grok
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter


grok.templatedir('templates')


class BaseView(grok.View):
    """Base class for View."""
    grok.baseclass()
    grok.layer(ICollectiveCartShoppingLayer)
    grok.require('zope2.View')


class ArticleView(BaseView):
    """Default view for Article."""
    grok.context(IArticle)
    grok.name('view')
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


class ArticleContainerView(BaseView):
    """Default view for ArticleContainer."""
    grok.context(IArticleContainer)
    grok.name('view')
    grok.template('article-container')


class CartView(core.browser.template.CartView, Message):
    """Cart View"""
    grok.layer(ICollectiveCartShoppingLayer)


class BaseCheckoutView(BaseView):
    grok.baseclass()
    grok.context(IShoppingSiteRoot)

    def update(self):
        if not IShoppingSite(self.context).cart_articles or (
            IShoppingSite(self.context).shipping_methods and not IShoppingSite(self.context).shipping_method):
            url = '{}/@@cart'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        else:
            self.request.set('disable_border', True)
            super(BaseCheckoutView, self).update()

    @property
    def cart(self):
        return IShoppingSite(self.context).cart


class BillingAndShippingView(BaseCheckoutView, Message):
    grok.name('billing-and-shipping')
    grok.template('billing-and-shipping')


class OrderConfirmationView(BaseCheckoutView, Message):
    grok.name('order-confirmation')
    grok.template('order-confirmation')

    def update(self):
        if not self.cart or not ICartAdapter(self.cart).is_addresses_filled:
            message = _(u'info_missing_from_addresses', default=u"Some information is missing from addresses.")
            IStatusMessage(self.request).addStatusMessage(message, type='info')
            url = '{}/@@billing-and-shipping'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        super(OrderConfirmationView, self).update()


class ThanksView(BaseCheckoutView, Message):
    """View for thank for order."""
    grok.name('thanks')
    grok.template('thanks')

    def update(self):
        super(ThanksView, self).update()
        context = aq_inner(self.context)
        form = self.request.form
        if form.get('form.buttons.ConfirmOrder') is not None:
            if IShoppingSite(self.context).get_brain_for_text('confirmation-terms-message') and form.get('accept-terms') is None:
                url = '{}/@@order-confirmation'.format(context.absolute_url())
                return self.request.response.redirect(url)
            else:
                self.cart_id = self.cart.id
                workflow = getToolByName(context, 'portal_workflow')
                workflow.doActionFor(self.cart, 'ordered')

        elif form.get('form.buttons.back') is not None:
            portal_state = getMultiAdapter((self.context, self.request), name="plone_portal_state")
            url = '{}/@@billing-and-shipping'.format(portal_state.navigation_root_url())
            return self.request.response.redirect(url)

        else:
            url = '{}/@@order-confirmation'.format(context.absolute_url())
            return self.request.response.redirect(url)

    def order_url(self):
        membership = getToolByName(self.context, 'portal_membership')
        return '{}?order_number={}'.format(membership.getHomeUrl(), self.cart_id)


class StockListView(BaseView):
    """View to show list of Article stock."""
    grok.context(core.interfaces.IArticle)
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


class CustomerInfoView(BaseView):
    """View for Customer Info."""
    grok.context(ICustomerInfo)
    grok.name('view')
    grok.template('customer-info')
