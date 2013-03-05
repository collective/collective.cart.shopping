# from collective.cart.shopping.event import ShippingAddressConfirmedEvent
# from zope.event import notify
from Acquisition import aq_inner
from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation import validation
from StringIO import StringIO
from collective.behavior.stock.interfaces import IStock as IStockBehavior
from collective.cart.core.browser.template import BaseCheckOutView as BaseBaseCheckOutView
from collective.cart.core.browser.template import CartView as BaseCartView
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping import _
from collective.cart.shopping.browser.base import Message
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import ICustomerInfo
from collective.cart.shopping.interfaces import IPriceUtility
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.stock.interfaces import IStock
from datetime import datetime
from five import grok
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from zope.component import getMultiAdapter
from zope.component import getUtility

import csv


grok.templatedir('templates')


class BaseView(grok.View):
    """Base class for View."""
    grok.baseclass()
    grok.layer(ICollectiveCartShoppingLayer)
    grok.require('zope2.View')


class BaseArticleView(BaseView):
    """Base class for Article"""
    grok.baseclass()
    grok.context(IArticle)

    @property
    @memoize
    def title(self):
        return IArticleAdapter(self.context).title


class ArticleView(BaseArticleView):
    """Default view for Article"""
    grok.name('view')
    grok.template('article')

    @property
    def images(self):
        results = []
        brains = IArticleAdapter(self.context).get_brains(IATImage, depth=1, sort_on='getObjPositionInParent')
        if brains:
            for brain in brains:
                results.append({
                    'description': brain.Description,
                    'title': brain.Title,
                    'url': brain.getURL(),
                })
        return results

    @property
    def gross(self):
        return IArticleAdapter(self.context).gross

    @property
    def discount_end(self):
        return IArticleAdapter(self.context).discount_end

    @property
    def image_url(self):
        return IArticleAdapter(self.context).image_url


class StockView(BaseArticleView):
    """View to show and manage article's stock."""
    grok.name('stock')
    grok.require('cmf.ModifyPortalContent')
    grok.template('stock')

    @property
    def stock(self):
        return IStockBehavior(self.context).stock

    @property
    def stocks(self):
        adapter = IArticleAdapter(self.context)
        res = []
        for item in adapter.get_content_listing(IStock, depth=1, sort_on='created', sort_order='descending'):
            res.append({
                'created': adapter.ulocalized_time(item.created),
                'current_stock': item.stock,
                'description': item.Description(),
                'initial_stock': item.initial_stock,
                'money': item.money,
                'title': item.Title(),
                'oid': item.id,
                'url': item.getURL(),
            })
        return res

    @property
    def add(self):
        stock = IStockBehavior(self.context)
        maximum = stock.initial_stock - stock.stock
        if maximum == 0:
            return None

        return {
            'max': maximum,
            'size': len(str(maximum)),
        }

    @property
    def subtract(self):
        maximum = self.stock
        if maximum == 0:
            return None
        return {
            'max': maximum,
            'size': len(str(maximum)),
        }

    def update(self):
        form = self.request.form
        url = getMultiAdapter((self.context, self.request), name="plone_context_state").current_base_url()
        stock = IStockBehavior(self.context)

        if form.get('form.buttons.QuickAdd') is not None:
            value = form.get('quick-add')
            validate = validation.validatorFor('isInt')
            maximum = self.add['max']
            if validate(value) != 1:
                message = _(u'add_less_than_number', default=u'Add less than ${number}.', mapping={'number': maximum})
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
            else:
                value = int(value)
                message = _(u'successfully_added_number', default=u'Successfully added ${number} pc(s).', mapping={
                    'number': stock.add_stock(value)})
                IStatusMessage(self.request).addStatusMessage(message, type='info')
            return self.request.response.redirect(url)

        elif form.get('form.buttons.QuickSubtract') is not None:
            value = form.get('quick-subtract')
            validate = validation.validatorFor('isInt')
            maximum = self.subtract['max']
            if validate(value) != 1:
                message = _(u'subtract_less_than_number', default=u'Subtract less than ${number}.', mapping={'number': maximum})
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
            else:
                value = int(value)
                message = _(u'successfully_subtracted_number', default=u'Successfully subtracted ${number} pc(s).', mapping={
                    'number': stock.sub_stock(value)})
                IStatusMessage(self.request).addStatusMessage(message, type='info')
            return self.request.response.redirect(url)

        elif form.get('form.buttons.AddNewStock') is not None:
            url = '{}/++add++collective.cart.stock.Stock'.format(self.context.absolute_url())
            return self.request.response.redirect(url)

        elif form.get('form.buttons.Remove') is not None:
            ids = [form.get('form.buttons.Remove')]
            self.context.manage_delObjects(ids)
            return self.request.response.redirect(url)


class ArticleContainerView(BaseView):
    """Default view for ArticleContainer"""
    grok.context(IArticleContainer)
    grok.name('view')
    grok.template('article-container')


class BaseCheckOutView(BaseBaseCheckOutView):
    """Base class for check out view"""
    grok.baseclass()
    grok.layer(ICollectiveCartShoppingLayer)

    @property
    def shopping_site(self):
        return IShoppingSite(self.context)

    def update(self):
        super(BaseCheckOutView, self).update()

        if self.cart_articles:
            articles = self.cart_articles.copy()
            number_of_articles = len(articles)
            for key in self.cart_articles:
                obj = self.shopping_site.get_object(UID=key)
                if obj and IStockBehavior(obj).stock == 0:
                    del articles[key]

            if len(articles) != number_of_articles:
                session = self.shopping_site.getSessionData(create=False)
                session.set('collective.cart.core', {'articles': articles})

            if not articles or (self.shopping_site.shipping_methods and not self.shopping_site.shipping_method):
                url = '{}/@@cart'.format(self.context.absolute_url())
                return self.request.response.redirect(url)


class CartView(BaseCheckOutView, BaseCartView, Message):
    """Cart View"""

    def update(self):
        shopping_site = IShoppingSite(self.context)
        if shopping_site.shipping_method is None:
            shopping_site.update_shipping_method()
        super(CartView, self).update()


class BillingAndShippingView(BaseCheckOutView, Message):
    grok.name('billing-and-shipping')
    grok.template('billing-and-shipping')


class ShippingInfoView(BaseCheckOutView, Message):
    """View for editing shipping info which checkout"""
    grok.name('shipping-info')
    grok.template('shipping-info')

    @property
    def shipping_info(self):
        return self.shopping_site.get_info('shipping')

    def update(self):
        form = self.request.form
        shop_url = self.context.absolute_url()
        if form.get('form.buttons.back') is not None:
            url = '{}/@@billing-and-shipping'.format(shop_url)
            return self.request.response.redirect(url)
        if form.get('form.to.confirmation') is not None:
            current_url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()
            first_name = form.get('first-name')
            if not first_name:
                message = _('First name is missing.')
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
                return self.request.response.redirect(current_url)
            last_name = form.get('last-name')
            if not last_name:
                message = _('Last name is missing.')
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
                return self.request.response.redirect(current_url)
            email = form.get('email')
            email_validation = validation.validatorFor('isEmail')
            if email_validation(email) != 1:
                message = _('Invalid e-mail address.')
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
                return self.request.response.redirect(current_url)
            street = form.get('street')
            if not street:
                message = _('Street address is missing.')
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
                return self.request.response.redirect(current_url)
            city = form.get('city')
            if not city:
                message = _('City is missing.')
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
                return self.request.response.redirect(current_url)
            phone = form.get('phone')
            if not phone:
                message = _('Phone number is missing.')
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
                return self.request.response.redirect(current_url)
            else:
                organization = form.get('organization')
                vat = form.get('vat')
                post = form.get('post')

                data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'organization': organization,
                    'vat': vat,
                    'email': email,
                    'street': street,
                    'post': post,
                    'city': city,
                    'phone': phone,
                }

                shipping = self.shopping_site.get_address('shipping')
                if shipping is None:
                    self.shopping_site.update_cart('shipping', data)
                else:
                    for key in data:
                        if shipping[key] != data[key]:
                            shipping[key] = data[key]
                    self.shopping_site.update_cart('shipping', shipping)

                # cart = self.shopping_site.cart
                # notify(ShippingAddressConfirmedEvent(cart))

                url = '{}/@@order-confirmation'.format(shop_url)
                return self.request.response.redirect(url)


class OrderConfirmationView(BaseCheckOutView, Message):
    grok.name('order-confirmation')
    grok.template('order-confirmation')

    def update(self):
        if not self.shopping_site.is_addresses_filled:
            message = _(u'info_missing_from_addresses', default=u"Some information is missing from addresses.")
            IStatusMessage(self.request).addStatusMessage(message, type='info')
            url = '{}/@@billing-and-shipping'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        super(OrderConfirmationView, self).update()


class ThanksView(OrderConfirmationView, Message):
    """View for thank for order."""
    grok.name('thanks')
    grok.template('thanks')

    def update(self):
        super(ThanksView, self).update()
        context = aq_inner(self.context)
        context_url = context.absolute_url()
        form = self.request.form
        if form.get('form.buttons.ConfirmOrder') is not None:
            if self.shopping_site.get_brain_for_text('confirmation-terms-message') and form.get('accept-terms') is None:
                message = _(u'need_to_accept_terms', default=u"You need to accept the terms to process the order.")
                IStatusMessage(self.request).addStatusMessage(message, type='info')
                url = '{}/@@order-confirmation'.format(context_url)
                return self.request.response.redirect(url)
            else:
                cart = self.shopping_site.create_cart()
                self.cart_id = cart.id
                workflow = getToolByName(context, 'portal_workflow')
                workflow.doActionFor(cart, 'ordered')

        elif form.get('form.buttons.back') is not None:
            url = '{}/@@billing-and-shipping'.format(context_url)
            return self.request.response.redirect(url)

        else:
            url = '{}/@@order-confirmation'.format(context_url)
            return self.request.response.redirect(url)

    @property
    def order_url(self):
        membership = getToolByName(self.context, 'portal_membership')
        return '{}?order_number={}'.format(membership.getHomeUrl(), self.cart_id)


class ArticleListingView(BaseView):
    """List for all the articles."""
    grok.context(IShoppingSiteRoot)
    grok.name('article-listing')
    grok.require('cmf.ModifyPortalContent')
    grok.template('article-listing')

    @property
    @memoize_contextless
    def table_headers(self):
        return (
            _(u'SKU'),
            _(u'Name'),
            _(u'Price'),
            _(u'Stock'),
            _(u'Subtotal'))

    @property
    def articles(self):
        res = []
        for item in IShoppingSite(self.context).get_content_listing(IArticle, sort_on='sku'):
            obj = item.getObject()
            article = IArticleAdapter(obj)
            sbehavior = IStockBehavior(obj)
            stock = sbehavior.stock
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
                'title': article.title,
                'url': item.getURL(),
            })
        return res

    def update(self):
        self.request.set('disable_plone.leftcolumn', True)
        self.request.set('disable_plone.rightcolumn', True)

    def __call__(self):
        if self.request.form.get('form.buttons.Export', None) is not None:
            out = StringIO()
            writer = csv.writer(out, delimiter='|', quoting=csv.QUOTE_MINIMAL)
            plone = self.context.restrictedTraverse('@@plone')
            encoding = plone.site_encoding()
            headers = [self.context.translate(_(header)).encode(encoding) for header in self.table_headers]
            writer.writerow(headers)

            for article in self.articles:
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
        else:
            return super(ArticleListingView, self).__call__()


class CustomerInfoView(BaseView):
    """View for Customer Info."""
    grok.context(ICustomerInfo)
    grok.name('view')
    grok.template('customer-info')
