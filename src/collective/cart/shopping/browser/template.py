from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from StringIO import StringIO
from collective.base.view import BaseFormView
from collective.behavior.stock.interfaces import IStock as IStockBehavior
from collective.cart.shopping import _
from collective.cart.shopping.browser.base import Message
from collective.cart.shopping.browser.interfaces import IArticleContainerView
from collective.cart.shopping.browser.interfaces import IArticleListingView
from collective.cart.shopping.browser.interfaces import IArticleView
from collective.cart.shopping.browser.interfaces import IBaseArticleView
from collective.cart.shopping.browser.interfaces import IBaseOrderMailTemplateView
from collective.cart.shopping.browser.interfaces import IBillingAndShippingView
from collective.cart.shopping.browser.interfaces import ICartView
from collective.cart.shopping.browser.interfaces import ICheckOutView
from collective.cart.shopping.browser.interfaces import ICustomerInfoView
from collective.cart.shopping.browser.interfaces import IOrderConfirmationView
from collective.cart.shopping.browser.interfaces import IStockView
from collective.cart.shopping.browser.interfaces import IThanksView
from collective.cart.shopping.browser.interfaces import IToCustomerOrderMailTemplateView
from collective.cart.shopping.browser.interfaces import IToShopOrderMailTemplateView
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IPriceUtility
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.stock.interfaces import IStock
from datetime import datetime
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from zope.component import getUtility
from zope.interface import implements

import csv


class BaseArticleView(BaseFormView):
    """Base class for Article"""
    implements(IBaseArticleView)

    def adapter(self):
        """Returns ArticleAdapter"""
        return IArticleAdapter(self.context)

    @memoize
    def title(self):
        """Returns title"""
        return self.adapter().title()

    def __call__(self):
        return self.template()


class ArticleView(BaseArticleView):
    """Default view for content type: collective.cart.core.Article"""
    implements(IArticleView)

    def description(self):
        """Returns description"""
        return self.context.description


class StockView(BaseArticleView):
    """Stock view for content type: collective.cart.core.Article"""
    implements(IStockView)

    def stock(self):
        """Returns stock

        :rtype: int
        """
        return IStockBehavior(self.context).stock()

    def stocks(self):
        """Returns content listing of stock"""
        return self.adapter().get_content_listing(IStock, depth=1, sort_on='getObjPositionInParent', sort_order='descending')

    def title(self):
        """Returns title"""
        title = safe_unicode(super(StockView, self).title())
        return _(u'stock_of_article', u'${title}: ${stock} pcs',
            mapping={'title': title, 'stock': self.stock()})

    def description(self):
        if not self.stocks():
            return _(u'description_no_stocks_available', u'There are no stocks available.')


class ArticleContainerView(BrowserView):
    """Default view for content type: collective.cart.core.ArticleContainer"""
    implements(IArticleContainerView)

    __call__ = ViewPageTemplateFile('templates/article-container.pt')


class CheckOutView(BaseFormView, Message):
    """Base view class for check out"""
    implements(ICheckOutView)

    def description(self):
        """Returns description"""
        message = self.message()
        if message:
            return message.get('description')

    def __call__(self):
        super(CheckOutView, self).__call__()
        IShoppingSite(self.context).clean_articles_in_cart()

        shopping_site = self.shopping_site()
        if not self.cart_articles() or (shopping_site.shipping_methods() and not shopping_site.shipping_method()):

            cart_url = '{}/@@cart'.format(self.context.absolute_url())
            current_base_url = self.context.restrictedTraverse("@@plone_context_state").current_base_url()

            if cart_url != current_base_url:
                return self.request.response.redirect(cart_url)

    def shopping_site(self):
        """Returns adapter: ShoppingSite

        :rtype: collective.cart.shopping.adapter.interface.ShoppingSite
        """
        return IShoppingSite(self.context)

    def cart_articles(self):
        """Returns articles in cart

        :rtype: dict
        """
        return self.shopping_site().cart_articles()


class CartView(CheckOutView):
    """View for cart"""
    implements(ICartView)
    title = _(u'Cart')

    def __call__(self):
        shopping_site = self.shopping_site()
        if shopping_site.shipping_method() is None:
            shopping_site.update_shipping_method()
        if not super(CartView, self).__call__():
            return self.template()


class BillingAndShippingView(CheckOutView):
    """View for billing and shipping"""
    implements(IBillingAndShippingView)
    title = _('Addresses')

    def __call__(self):
        if not super(BillingAndShippingView, self).__call__():
            return self.template()


class OrderConfirmationView(CheckOutView):
    """View for order confirmation"""

    implements(IOrderConfirmationView)
    title = _(u'Confirmation')

    def __call__(self):
        if not self.shopping_site().is_addresses_filled():
            message = _(u'info_missing_from_addresses', default=u"Some information is missing from addresses.")
            IStatusMessage(self.request).addStatusMessage(message, type='info')
            url = '{}/@@billing-and-shipping'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        if not super(OrderConfirmationView, self).__call__():
            return self.template()


class ThanksView(CheckOutView):
    """View for thanks"""
    implements(IThanksView)
    template = ViewPageTemplateFile('templates/thanks.pt')

    def __call__(self):

        shopping_site = self.shopping_site()
        # Create cart to cart container from session.
        order = shopping_site.create_order()

        if order is None:
            url = self.context.absolute_url()
            return self.request.response.redirect(url)

        self.order_id = order.id
        # Change state of cart from created to ordered.
        workflow = getToolByName(self.context, 'portal_workflow')
        workflow.doActionFor(order, 'ordered')
        # Reduce stocks from ordered stocks.
        shopping_site.reduce_stocks()
        # Clear articles from session.
        shopping_site.remove_from_cart('articles')

        return self.template()


class ArticleListingView(BaseFormView):
    """View for listing all the articles"""
    implements(IArticleListingView)

    title = _(u'Article Listing')

    @memoize_contextless
    def table_headers(self):
        """Returns headers for table

        :rtype: tuple
        """
        return (
            _(u'SKU'),
            _(u'Name'),
            _(u'Price'),
            _(u'Stock'),
            _(u'Subtotal'))

    def articles(self):
        """Returns list of dictionary of articles in shop

        :rtype: list
        """
        res = []
        for item in IShoppingSite(self.context).get_content_listing(IArticle, sort_on='sku'):
            obj = item.getObject()
            article = IArticleAdapter(obj)
            sbehavior = IStockBehavior(obj)
            stock = sbehavior.stock()
            stocks = sbehavior.stocks()
            if stocks:
                price = stocks[-1].price
                subtotal = price * stock
                price = getUtility(IPriceUtility, name="string")(price)
                subtotal = getUtility(IPriceUtility, name="string")(subtotal)
            else:
                price = subtotal = 'N/A'
            res.append({
                'price': price,
                'sku': item.sku,
                'stock': stock,
                'subtotal': subtotal,
                'title': article.title(),
                'url': item.getURL(),
            })
        return res

    def __call__(self):
        self.request.set('disable_plone.leftcolumn', True)
        self.request.set('disable_plone.rightcolumn', True)

        if self.request.form.get('form.buttons.Export', None) is not None:
            out = StringIO()
            writer = csv.writer(out, delimiter='|', quoting=csv.QUOTE_MINIMAL)
            plone = self.context.restrictedTraverse('@@plone')
            encoding = plone.site_encoding()
            headers = [self.context.translate(_(header)).encode(encoding) for header in self.table_headers()]
            writer.writerow(headers)

            for article in self.articles():
                writer.writerow((
                    article['sku'].encode(encoding),
                    article['title'],
                    article['price'],
                    article['stock'],
                    article['subtotal']))

            filename = 'stock-{}.csv'.format(datetime.now().isoformat())
            cd = 'attachment; filename="{}"'.format(filename)
            self.request.response.setHeader('Content-Type', 'text/csv')
            self.request.response.setHeader("Content-Disposition", cd)
            return out.getvalue()

        return self.template()


class CustomerInfoView(BrowserView):
    """View for Customer Info."""
    implements(ICustomerInfoView)
    __call__ = ViewPageTemplateFile('templates/customer-info.pt')


class BaseOrderMailTemplateView(BrowserView, Message):
    """Base view for order template used for sending e-mail"""
    implements(IBaseOrderMailTemplateView)
    template = ViewPageTemplateFile('templates/order-mail-template.pt')

    is_for_customer = True

    def __call__(self, **items):
        self.items = items
        return self.template()

    def message(self):
        """Returns message converted from html to text

        :rtype: str
        """
        if self.is_for_customer:
            message = super(BaseOrderMailTemplateView, self).message()
            if message:
                transforms = getToolByName(self.context, 'portal_transforms')
                html = message['text']
                message['text'] = transforms.convert('html_to_text', html).getData().strip()
                return message

    def link_to_order(self):
        """Returns link to order

        :rtype: str
        """
        if self.is_for_customer:
            if self.context.restrictedTraverse('@@plone_portal_state').anonymous():
                return False
            else:
                return IShoppingSite(self.context).link_to_order(self.items['number'])
        else:
            return IShoppingSite(self.context).get_order(self.items['number']).absolute_url()


class ToCustomerOrderMailTemplateView(BaseOrderMailTemplateView):
    """Mail template used to send e-mail to customer"""
    implements(IToCustomerOrderMailTemplateView)


class ToShopOrderMailTemplateView(BaseOrderMailTemplateView):
    """Mail template used to send email to shop"""
    implements(IToShopOrderMailTemplateView)
    is_for_customer = False
