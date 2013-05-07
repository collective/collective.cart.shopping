from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation import validation
from collective.behavior.stock.interfaces import IStock
from collective.behavior.vat.interfaces import IAdapter as IVATAdapter
from collective.cart.core.browser.interfaces import ICartArticleListingViewlet
from collective.cart.core.browser.viewlet import AddToCartViewlet as BaseBaseAddToCartViewlet
from collective.cart.core.browser.viewlet import CartArticleListingViewlet as BaseCartArticleListingViewlet
from collective.cart.shopping import _
from collective.cart.shopping.browser.base import Message
from collective.cart.shopping.browser.interfaces import IAddSubtractStockViewlet
from collective.cart.shopping.browser.interfaces import IAddToCartViewlet
from collective.cart.shopping.browser.interfaces import IArticleImagesViewlet
from collective.cart.shopping.browser.interfaces import IArticlesInArticleContainerViewlet
from collective.cart.shopping.browser.interfaces import IArticlesInArticleViewlet
from collective.cart.shopping.browser.interfaces import IBaseAddToCartViewlet
from collective.cart.shopping.browser.interfaces import IBaseArticleViewlet
from collective.cart.shopping.browser.interfaces import IBaseCheckOutButtonsViewlet
from collective.cart.shopping.browser.interfaces import IBillingAndShippingBillingAddressViewlet
from collective.cart.shopping.browser.interfaces import IBillingAndShippingCheckOutButtonsViewlet
from collective.cart.shopping.browser.interfaces import IBillingAndShippingShippingAddressViewlet
from collective.cart.shopping.browser.interfaces import IBillingAndShippingShippingMethodsViewlet
from collective.cart.shopping.browser.interfaces import ICartArticlesTotalViewlet
from collective.cart.shopping.browser.interfaces import ICartCheckOutButtonsViewlet
from collective.cart.shopping.browser.interfaces import ICheckOutFlowViewlet
from collective.cart.shopping.browser.interfaces import IOrderConfirmationCartArticleListingViewlet
from collective.cart.shopping.browser.interfaces import IOrderConfirmationCheckOutButtonsViewlet
from collective.cart.shopping.browser.interfaces import IOrderConfirmationShippingMethodViewlet
from collective.cart.shopping.browser.interfaces import IOrderConfirmationTermsViewlet
from collective.cart.shopping.browser.interfaces import IOrderConfirmationTotalViewlet
from collective.cart.shopping.browser.interfaces import IRelatedArticlesViewlet
from collective.cart.shopping.browser.interfaces import IStockListingViewlet
from collective.cart.shopping.event import BillingAddressConfirmedEvent
from collective.cart.shopping.event import ShippingAddressConfirmedEvent
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import ICartArticleMultiAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IShoppingSiteMultiAdapter
from collective.cart.stock.interfaces import IStock as IStockContent
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.layout.viewlets.common import ViewletBase
from plone.uuid.interfaces import IUUID
from zExceptions import Forbidden
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import implements


class ArticlesInArticleContainerViewlet(ViewletBase):
    """Viewlet for content type: collective.cart.shopping.ArticleContainer

    Shows listing of articles within context
    """
    implements(IArticlesInArticleContainerViewlet)
    index = ViewPageTemplateFile('viewlets/articles-in-article-container.pt')

    def articles(self):
        """Returns listing of articles

        :rtype: list
        """
        res = []
        shopping_site = IShoppingSite(self.context)
        for item in shopping_site.get_content_listing(IArticle, depth=1, sort_on='getObjPositionInParent'):
            style_class = 'normal'
            obj = item.getObject()
            adapter = IArticleAdapter(obj)
            discount_available = adapter.discount_available()
            if discount_available:
                style_class = 'discount'
            res.append({
                'discount-available': discount_available,
                'gross': shopping_site.format_money(adapter.gross()),
                'money': shopping_site.format_money(item.money),
                'class': style_class,
                'title': item.Title(),
                'url': item.getURL(),
            })
        return res


class BaseArticleViewlet(ViewletBase):
    """Base viewlet class for content type: collective.cart.core.Article"""
    implements(IBaseArticleViewlet)

    def title(self):
        """Returns title"""
        return self.view.adapter().title()


class ArticleImagesViewlet(BaseArticleViewlet):
    """Viewlet for content type: collective.cart.core.Article

    Shows images
    """
    implements(IArticleImagesViewlet)
    index = ViewPageTemplateFile('viewlets/article-images.pt')

    def images(self):
        """Returns images"""
        results = []
        brains = self.view.adapter().get_brains(IATImage, depth=1, sort_on='getObjPositionInParent')
        if brains:
            for brain in brains:
                results.append({
                    'description': brain.Description,
                    'title': brain.Title,
                    'url': brain.getURL(),
                })
        return results

    def image_url(self):
        """Returns image url"""
        return self.view.adapter().image_url()


class BaseAddToCartViewlet(BaseArticleViewlet, BaseBaseAddToCartViewlet):
    """Base viewlet class for add to cart"""
    implements(IBaseAddToCartViewlet)

    def quantity_size(self):
        """Returns size for quantity field

        :rtype: int
        """
        if getattr(self, 'quantity_max', None) is not None:
            return len(str(self.quantity_max()))


class AddToCartViewlet(BaseAddToCartViewlet):
    """Viewlet for add to cart"""
    implements(IAddToCartViewlet)
    index = ViewPageTemplateFile('viewlets/add-to-cart.pt')

    def update(self):
        if self.available():
            getMultiAdapter((self.context, self.request), IShoppingSiteMultiAdapter).add_to_cart()

    def quantity_max(self):
        """Max quantity

        :rtype: int
        """
        return self.view.adapter().quantity_max()

    def soldout(self):
        """Returns True if sold out else False

        :rtype: bool
        """
        return self.view.adapter().soldout()

    def available(self):
        """Returns True if available else False

        :rtype: bool
        """
        if self.articles():
            return False
        return self.context.salable or self.view.adapter().articles(salable=True)

    def uuid(self):
        """Returns uuid

        :rtype: str
        """
        return IUUID(self.context)

    def gross(self):
        """Returns localized discount money or original gross money

        :rtype: unicode
        """
        gross = self.view.adapter().gross()
        return IShoppingSite(self.context).format_money(gross)

    def money(self):
        """Returns localized original gross money

        :rtype: unicode
        """
        return IShoppingSite(self.context).format_money(self.context.money)

    def vat_rate(self):
        """Returns localized VAT rate

        :rtype: unicode
        """
        return IVATAdapter(self.context).percent(self.context.vat_rate)

    def discount_end(self):
        """Returns end of date for discount

        :rtype: unicode
        """
        return self.view.adapter().discount_end()

    def subarticles(self):
        """Returns list of subarticles

        :rtype: list
        """
        return self.view.adapter().subarticles()

    def articles(self):
        """Returns brains of articles

        :rtype: brains
        """
        if not self.context.use_subarticle:
            return self.view.adapter().articles()


class ArticlesInArticleViewlet(AddToCartViewlet):
    """Viewlet for content type: collective.cart.core.Article"""
    implements(IArticlesInArticleViewlet)
    index = ViewPageTemplateFile('viewlets/articles-in-article.pt')

    def available(self):
        """Returns True if available else False

        :rtype: bool
        """
        if self.articles():
            return True
        return False

    def articles(self):
        """Returns list of dictionary of articles

        :rtype: list
        """
        res = []
        shopping_site = IShoppingSite(self.context)
        articles = super(ArticlesInArticleViewlet, self).articles()
        if articles:
            for item in IContentListing(articles):
                obj = item.getObject()
                adapter = IArticleAdapter(obj)
                soldout = adapter.soldout()
                quantity_max = adapter.quantity_max()
                numbers = xrange(1, quantity_max + 1)
                quantity_size = len(str(quantity_max))
                subarticles = []
                if obj.use_subarticle:
                    subarticles = adapter.subarticles()
                res.append({
                    'description': item.Description(),
                    'discount_end': adapter.discount_end(),
                    'gross': shopping_site.format_money(adapter.gross()),
                    'id': item.getId(),
                    'image_url': adapter.image_url(),
                    'money': shopping_site.format_money(item.money),
                    'numbers': numbers,
                    'quantity_max': quantity_max,
                    'quantity_size': quantity_size,
                    'soldout': soldout,
                    'subarticles': subarticles,
                    'title': adapter.title(),
                    'url': item.getURL(),
                    'uuid': item.uuid(),
                    'vat_rate': IVATAdapter(self.context).percent(item.vat_rate)
                })
        return res


class RelatedArticlesViewlet(ViewletBase):
    """Viewlet for content type: collective.cart.core.Article

    Shows related articles
    """
    implements(IRelatedArticlesViewlet)
    index = ViewPageTemplateFile('viewlets/related-articles.pt')

    def articles(self):
        """Returns list of dictionary of articles

        :rtype: list
        """
        res = []

        context = aq_inner(self.context)
        if not getattr(context, 'related_articles', None):
            context = aq_parent(context)
            if not getattr(context, 'related_articles', None):
                context = aq_parent(context)

        if getattr(context, 'related_articles', None):
            shopping_site = IShoppingSite(self.context)
            path = shopping_site.shop_path()
            for uuid in context.related_articles:
                obj = shopping_site.get_object(IArticle, UID=uuid, path=path, review_state='published')
                if obj is not None:
                    art = IArticleAdapter(obj)
                    res.append({
                        'gross': art.gross(),
                        'image_url': art.image_url(),
                        'title': art.title(),
                        'url': obj.absolute_url(),
                    })
        return res[:4]


class AddSubtractStockViewlet(BaseArticleViewlet):
    """Viewlet for add and subtract stock"""
    implements(IAddSubtractStockViewlet)
    index = ViewPageTemplateFile('viewlets/add-subtract-stock.pt')

    def stock(self):
        """Returns stock

        :rtype: int
        """
        return IStock(self.context).stock()

    def stocks(self):
        """Returns list of dictionary of stocks

        :rtype: list
        """
        res = []
        adapter = self.view.adapter()
        toLocalizedTime = self.context.restrictedTraverse('@@plone').toLocalizedTime
        for item in adapter.get_content_listing(IStockContent, depth=1, sort_on='getObjPositionInParent', sort_order='descending'):
            res.append({
                'created': toLocalizedTime(item.created),
                'current_stock': item.stock,
                'description': item.Description(),
                'initial_stock': item.initial_stock,
                'money': item.money,
                'title': item.Title(),
                'oid': item.id,
                'url': item.getURL(),
            })
        return res

    def add(self):
        """Returns attributes: max and size for input: add

        :rtype: dict
        """
        stock = IStock(self.context)
        maximum = stock.initial_stock() - stock.stock()
        if maximum == 0:
            return None

        return {
            'max': maximum,
            'size': len(str(maximum)),
        }

    def subtract(self):
        """Returns attributes: max and size for input: subtract

        :rtype: dict
        """
        maximum = self.stock()
        if maximum == 0:
            return None
        return {
            'max': maximum,
            'size': len(str(maximum)),
        }

    def update(self):
        form = self.request.form
        url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()
        stock = IStock(self.context)

        if form.get('form.buttons.QuickAdd') is not None:
            value = form.get('quick-add')
            validate = validation.validatorFor('isInt')
            maximum = self.add()['max']
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
            maximum = self.subtract()['max']
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


class StockListingViewlet(ViewletBase):
    """Viewlet for listing stock"""
    implements(IStockListingViewlet)
    index = ViewPageTemplateFile('viewlets/stock-listing.pt')

    def stocks(self):
        """Returns list of dictionary of stocks

        :rtype: list
        """
        res = []
        toLocalizedTime = self.context.restrictedTraverse('@@plone').toLocalizedTime
        for item in IArticleAdapter(self.context).get_content_listing(
            IStockContent, depth=1, sort_on='getObjPositionInParent', sort_order='descending'):
            res.append({
                'created': toLocalizedTime(item.created),
                'current_stock': item.stock,
                'description': item.Description(),
                'initial_stock': item.initial_stock,
                'money': item.money,
                'title': item.Title(),
                'oid': item.id,
                'url': item.getURL(),
            })
        return res

    def update(self):
        form = self.request.form
        oid = form.get('form.buttons.Remove')
        if oid is not None:
            stock = self.context[oid].stock
            url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()
            ids = [oid]
            self.context.manage_delObjects(ids)
            message = _(u'successfully_removed_stock', default=u'Successfully removed ${number} pc(s) of stock.', mapping={
                'number': stock})
            IStatusMessage(self.request).addStatusMessage(message, type='info')
            return self.request.response.redirect(url)


class CheckOutFlowViewlet(ViewletBase):
    """Viewlet for check out flow"""
    implements(ICheckOutFlowViewlet)
    index = ViewPageTemplateFile('viewlets/check-out-flow.pt')

    views = ['cart', 'billing-and-shipping', 'order-confirmation']

    def _get_title(self, view):
        """Returns title of view based on view name

        :param view: Name of view
        :type view: str
        """
        name = '{}-message'.format(view)
        brain = self.view.shopping_site().get_brain_for_text(name)
        if brain:
            return brain.Title
        else:
            return self.context.restrictedTraverse(view).title

    def available(self):
        return self.view.__name__ in self.views

    def items(self):
        """Returns list of dictionary of check out component

        :rtype: list
        """
        res = []
        view_name = self.view.__name__
        younger_views = self.views[:self.views.index(view_name)]
        for view in self.views:
            klass = view
            url = None
            if view == view_name:
                klass = u'{} current-step'.format(view)
            if view in younger_views:
                url = '{}/@@{}'.format(self.context.absolute_url(), view)
            res.append({
                'class': klass,
                'title': self._get_title(view),
                'url': url,
            })
        return res


class BaseCheckOutButtonsViewlet(ViewletBase):
    """Base viewlet class for check out buttons"""
    implements(IBaseCheckOutButtonsViewlet)
    index = ViewPageTemplateFile('viewlets/check-out-buttons.pt')

    def update(self):
        form = self.request.form
        views = ['cart', 'billing-and-shipping', 'order-confirmation', 'thanks']
        if form.get('form.buttons.CheckOut') is not None:

            authenticator = self.context.restrictedTraverse('@@authenticator')
            if not authenticator.verify():
                raise Forbidden()

            index = views.index(self.view.__name__) + 1
            url = '{}/@@{}'.format(self.context.absolute_url(), views[index])
            return url

        if form.get('form.buttons.Back') is not None:

            authenticator = self.context.restrictedTraverse('@@authenticator')
            if not authenticator.verify():
                raise Forbidden()

            index = views.index(self.view.__name__) - 1
            url = '{}/@@{}'.format(self.context.absolute_url(), views[index])

            return self.request.response.redirect(url)

    def buttons(self):
        """Returns list of dictionary of buttons

        :rtype: list
        """
        return [
            {
                'class': 'back',
                'formnovalidate': True,
                'name': 'form.buttons.Back',
                'title': _(u'Back'),
                'value': 'form.buttons.Back',
            },
            {
                'class': 'next',
                'formnovalidate': False,
                'name': 'form.buttons.CheckOut',
                'title': _(u'Next'),
                'value': 'form.buttons.CheckOut',
            }
        ]

    def available(self):
        """Returns True if available else False

        :rtype: bool
        """
        if self.view.cart_articles():
            return True
        else:
            return False


class CartArticleListingViewlet(BaseCartArticleListingViewlet):
    """Viewlet for listing cart articles"""
    implements(ICartArticleListingViewlet)
    index = ViewPageTemplateFile('viewlets/cart-article-listing.pt')

    def update(self):
        super(CartArticleListingViewlet, self).update()
        form = self.request.form
        uuid = form.get('form.buttons.UpdateArticle')

        if uuid is not None:

            authenticator = self.context.restrictedTraverse('@@authenticator')
            if not authenticator.verify():
                raise Forbidden()

            quantity = form.get(uuid)
            validate = validation.validatorFor('isInt')

            if quantity is not None and validate(quantity) == 1 and int(quantity) >= 0:
                quantity = int(quantity)
                shopping_site = self.view.shopping_site()
                carticle = shopping_site.get_cart_article(uuid)
                adapter = getMultiAdapter((self.context, carticle), ICartArticleMultiAdapter)
                article = adapter.orig_article()
                if quantity == 0:
                    shopping_site.remove_cart_articles(uuid)
                elif article:
                    stock = IStock(article).stock()
                    reducible_quantity = IStock(article).reducible_quantity

                    if stock > reducible_quantity:
                        stock = reducible_quantity

                    if quantity > stock:
                        quantity = stock
                        message = _(u'no_more_than_quantity',
                            default=u"No more than ${quantity} can be added to cart for ${title}",
                            mapping={'quantity': quantity, 'title': safe_unicode(carticle['title'])})
                        IStatusMessage(self.request).addStatusMessage(message, type='info')

                    if quantity != carticle['quantity']:
                        carticle['quantity'] = quantity

            else:
                message = _(u"Invalid quantity.")
                IStatusMessage(self.request).addStatusMessage(message, type='warn')

            url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()
            return self.request.response.redirect(url)

    def articles(self):
        """Returns list of articles to show in cart."""
        res = []
        shopping_site = IShoppingSite(self.context)
        for article in shopping_site.cart_article_listing():
            adapter = getMultiAdapter((self.context, article), ICartArticleMultiAdapter)
            article.update({
                'image_url': adapter.image_url(),
                'gross': shopping_site.format_money(article['gross']),
                'gross_subtotal': shopping_site.format_money(adapter.gross_subtotal()),
                'quantity_max': adapter.quantity_max(),
                'quantity_size': adapter.quantity_size(),
            })
            res.append(article)
        return res


class CartArticlesTotalViewlet(ViewletBase):
    """Viewlet to display total money of articles."""
    implements(ICartArticlesTotalViewlet)
    index = ViewPageTemplateFile('viewlets/cart-articles-total.pt')

    def articles_total(self):
        """Returns localized money of articles total

        :rtype: unicode
        """
        shopping_site = self.view.shopping_site()
        return shopping_site.format_money(shopping_site.articles_total())

    def available(self):
        """Returns True if articles in cart else False

        :rtype: bool
        """
        if self.view.shopping_site().cart_articles():
            return True
        else:
            return False


class CartCheckOutButtonsViewlet(BaseCheckOutButtonsViewlet):
    """Viewlet for check out buttons for cart"""
    implements(ICartCheckOutButtonsViewlet)

    def update(self):
        url = super(CartCheckOutButtonsViewlet, self).update()

        form = self.request.form
        if form.get('form.buttons.ClearCart') is not None:

            authenticator = self.context.restrictedTraverse('@@authenticator')
            if not authenticator.verify():
                raise Forbidden()

            uuids = self.view.shopping_site().cart_articles().keys()
            self.view.shopping_site().remove_cart_articles(uuids)
            url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()

        if url is not None:
            return self.request.response.redirect(url)

    def buttons(self):
        buttons = super(CartCheckOutButtonsViewlet, self).buttons()[1:]
        buttons.insert(0, {
            'class': 'clear',
            'formnovalidate': True,
            'name': 'form.buttons.ClearCart',
            'title': _(u'Clear'),
            'value': 'form.buttons.ClearCart',
        })
        return buttons


class BillingAndShippingBillingAddressViewlet(ViewletBase):
    """Viewlet class to show form to update billing address"""
    implements(IBillingAndShippingBillingAddressViewlet)
    index = ViewPageTemplateFile('viewlets/billing-and-shipping-billing-address.pt')

    def billing_info(self):
        """Returns dictionary of billing address

        :rtype: dict
        """
        return IShoppingSite(self.context).get_info('billing')


class BillingAndShippingShippingAddressViewlet(ViewletBase):
    """Viewlet class to show form component of shipping address"""
    implements(IBillingAndShippingShippingAddressViewlet)
    index = ViewPageTemplateFile('viewlets/billing-and-shipping-shipping-address.pt')

    def shipping_info(self):
        """Returns dictionary of shipping address

        :rtype: dict
        """
        return IShoppingSite(self.context).get_info('shipping')

    def billing_same_as_shipping(self):
        """Returns True if billing address is same as shipping address

        :rtype: bool
        """
        return IShoppingSite(self.context).cart().get('billing_same_as_shipping', True)


class BillingAndShippingShippingMethodsViewlet(ViewletBase):
    """Viewlet class to show form to update billing address"""
    implements(IBillingAndShippingShippingMethodsViewlet)
    index = ViewPageTemplateFile('viewlets/billing-and-shipping-shipping-methods.pt')

    def shipping_methods(self):
        """Returns list of dictionary of shipping methods

        :rtype: list
        """
        shopping_site = IShoppingSite(self.context)
        default_charset = getattr(getattr(getToolByName(
            self.context, 'portal_properties'), 'site_properties'), 'default_charset', 'utf-8')
        res = []
        for brain in shopping_site.shipping_methods():
            uuid = brain.UID
            orig_uuid = shopping_site.shipping_method()['uuid']

            if uuid == orig_uuid:
                shipping_gross_money = shopping_site.shipping_gross_money()
            else:
                shipping_gross_money = shopping_site.get_shipping_gross_money(uuid)

            if shipping_gross_money.amount == 0.0:
                title = brain.Title
            else:
                title = '{}  {}'.format(brain.Title, shopping_site.format_money(shipping_gross_money).encode(default_charset))

            res.append({
                'description': brain.Description,
                'checked': uuid == orig_uuid,
                'title': title,
                'uuid': uuid,
            })

        return res

    def single_shipping_method(self):
        """Returns True if there is only one shipping method else False

        :rtype: bool
        """
        return len(self.shipping_methods()) == 1


class BillingAndShippingCheckOutButtonsViewlet(BaseCheckOutButtonsViewlet):
    """Viewlet for check out buttons for @@billing-and-shipping"""
    implements(IBillingAndShippingCheckOutButtonsViewlet)

    def single_shipping_method(self):
        """Returns True if there is only one shipping method else False

        :rtype: bool
        """
        return len(self.view.shopping_site().shipping_methods()) == 1

    def update(self):
        url = super(BillingAndShippingCheckOutButtonsViewlet, self).update()

        form = self.request.form

        if form.get('form.buttons.CheckOut') is not None:

            current_url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()
            shopping_site = self.view.shopping_site()
            message = shopping_site.update_address('billing', form)
            if message is not None:
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
                url = current_url

            notify(BillingAddressConfirmedEvent(self.context))

            if form.get('billing-same-as-shipping', 'different') == 'same':
                shopping_site.update_cart('billing_same_as_shipping', True)
            else:
                shopping_site.update_cart('billing_same_as_shipping', False)

                message = shopping_site.update_address('shipping', form)
                if message is not None:
                    IStatusMessage(self.request).addStatusMessage(message, type='warn')
                    url = current_url

                notify(ShippingAddressConfirmedEvent(self.context))

            shipping_method = form.get('shipping-method')
            if not self.single_shipping_method() and not shipping_method:
                message = _(u'Select one shipping method.')
                IStatusMessage(self.request).addStatusMessage(message, type='warn')
                url = current_url

            else:
                shopping_site.update_shipping_method(shipping_method)

            return self.request.response.redirect(url)


class OrderConfirmationCartArticleListingViewlet(CartArticleListingViewlet):
    """Viewlet for cart articles for @@order-confirmation"""
    implements(IOrderConfirmationCartArticleListingViewlet)
    index = ViewPageTemplateFile('viewlets/order-confirmation-cart-article-listing.pt')


class OrderConfirmationShippingMethodViewlet(ViewletBase):
    """Viewlet for shipping method for @@order-confirmation"""
    implements(IOrderConfirmationShippingMethodViewlet)
    index = ViewPageTemplateFile('viewlets/order-confirmation-shipping-method.pt')

    def shipping_method(self):
        shopping_site = IShoppingSite(self.context)
        items = shopping_site.shipping_method().copy()
        if items['gross'].amount == 0.0:
            items['is_free'] = True
        else:
            items['is_free'] = False
        items['vat_rate'] = IVATAdapter(self.context).percent(items['vat_rate'])
        items['gross'] = shopping_site.format_money(items['gross'])
        return items


class OrderConfirmationTotalViewlet(ViewletBase):
    """Viewlet for total for @@order-confirmation"""
    implements(IOrderConfirmationTotalViewlet)
    index = ViewPageTemplateFile('viewlets/order-confirmation-total.pt')

    def total(self):
        """Returns localized total money

        :rtype: unicode
        """
        return IShoppingSite(self.context).locale_total()


class OrderConfirmationTermsViewlet(ViewletBase, Message):
    """Viewlet for terms for @@order-confirmation"""
    implements(IOrderConfirmationTermsViewlet)
    index = ViewPageTemplateFile('viewlets/order-confirmation-terms.pt')

    def message(self):
        return super(OrderConfirmationTermsViewlet, self).message('terms')


class OrderConfirmationCheckOutButtonsViewlet(BaseCheckOutButtonsViewlet):
    """Viewlet for check out buttons for @@order-confirmation"""
    implements(IOrderConfirmationCheckOutButtonsViewlet)

    def update(self):
        url = super(OrderConfirmationCheckOutButtonsViewlet, self).update()

        form = self.request.form
        if form.get('form.buttons.CheckOut') is not None:

            if self.view.shopping_site().get_brain_for_text('terms-message') and form.get('accept-terms') is None:
                message = _(u'need_to_accept_terms', default=u"You need to accept the terms to process the order.")
                IStatusMessage(self.request).addStatusMessage(message, type='info')
                url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()

            return self.request.response.redirect(url)


# class ThanksBelowContentViewletManager(BaseViewletManager):
#     """Viewlet manager for thanks below content."""
#     grok.name('collective.cart.shopping.thanks.belowcontent.manager')


# class CartContentViewlet(BaseCartContentViewlet):
#     """Viewlet to show customer info in cart."""
#     grok.layer(ICollectiveCartShoppingLayer)

#     @property
#     def order(self):
#         workflow = getToolByName(self.context, 'portal_workflow')
#         cart = IOrderAdapter(self.context)
#         return {
#             'articles': cart.articles,
#             'id': self.context.id,
#             'modified': cart.ulocalized_time(self.context.modified()),
#             'shipping_method': cart.locale_shipping_method(),
#             'state_title': workflow.getTitleForStateOnType(workflow.getInfoFor(self.context, 'review_state'), self.context.portal_type),
#             'title': self.context.Title(),
#             'total': cart.locale_total(),
#             'url': self.context.absolute_url(),
#             'billing_info': cart.get_address('billing'),
#             'shipping_info': cart.get_address('shipping'),
#             'registration_number': getattr(self.context, 'registration_number', None)
#         }


# class CartContentDescriptionViewlet(BaseCartContentViewlet):
#     """Viewlet to show description of cart."""
#     grok.name('collective.cart.shopping.order.description')
#     grok.template('cart-content-description')


# class ArticleContainerViewletManager(BaseViewletManager):
#     """Viewlet manager for ArticleContainer."""
#     grok.context(IArticleContainer)
#     grok.name('collective.cart.shopping.articlecontainer')


class MessageTextViewlet(ViewletBase, Message):
    """Viewlet to show message text for check out flow"""

    index = ViewPageTemplateFile('viewlets/message-text.pt')
