# -*- coding: utf-8 -*-
# from zope.event import notify
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation import validation
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.browser.viewlet import AddToCartViewlet as BaseBaseAddToCartViewlet
from collective.cart.core.browser.viewlet import CartArticlesViewlet as BaseBaseCartArticlesViewlet
from collective.cart.core.browser.viewlet import CartContentViewlet as BaseCartContentViewlet
from collective.cart.core.browser.viewlet import CartViewletManager
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping import _
from collective.cart.shopping.browser.base import Message
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICartArticleMultiAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IShoppingSiteMultiAdapter
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IBelowContent
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter


grok.templatedir('viewlets')


class BaseViewletManager(OrderedViewletManager, grok.ViewletManager):
    """Base class for viewlet manager in collective.cart.shopping package."""
    grok.baseclass()
    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartShoppingLayer)


class BaseViewlet(grok.Viewlet):
    """Base class for viewlet in collective.cart.shopping package."""
    grok.baseclass()
    grok.layer(ICollectiveCartShoppingLayer)
    grok.require('zope2.View')


class BaseShoppingSiteRootViewlet(BaseViewlet):
    """Base viewlet class for IShoppingSiteRoot"""
    grok.baseclass()
    grok.context(IShoppingSiteRoot)


class BaseArticleViewlet(BaseViewlet):
    """Base viewlet class for IArticle"""
    grok.baseclass()
    grok.context(IArticle)


class RelatedArticlesViewlet(BaseArticleViewlet):
    """Viewlet to show related articles for IArticle"""
    grok.name('collective.cart.shopping.related.articles')
    grok.template('related-articles')
    grok.view(IViewView)
    grok.viewletmanager(IBelowContent)

    def articles(self):
        if hasattr(self.context, 'relatedItems'):
            res = []
            workflow = getToolByName(self.context, 'portal_workflow')
            for article in self.context.relatedItems:
                obj = article.to_object
                if IArticle.providedBy(obj) and workflow.getInfoFor(obj, 'review_state') == 'published':
                    art = IArticleAdapter(obj)
                    res.append({
                        'gross': art.gross,
                        'image_url': art.image_url,
                        'title': art.title,
                        'url': obj.absolute_url(),
                    })
            return res[:4]


class AddToCartViewletManager(BaseViewletManager):
    """Viewlet manager for add to cart form in Article."""
    grok.context(IArticle)
    grok.name('collective.cart.shopping.add.to.cart.manager')


class BaseAddToCartViewlet(BaseBaseAddToCartViewlet):
    """Base class for add to cart viewlet."""
    grok.baseclass()
    grok.layer(ICollectiveCartShoppingLayer)
    grok.viewletmanager(AddToCartViewletManager)

    @property
    def quantity_size(self):
        """Size for quantity field."""
        if getattr(self, 'quantity_max', None) is not None:
            return len(str(self.quantity_max))


class AddToCartViewlet(BaseAddToCartViewlet):
    """Viewlet to show add to cart form for salable article.

    Can also add with certain number of quantity.
    """

    def update(self):
        getMultiAdapter((self.context, self.request), IShoppingSiteMultiAdapter).add_to_cart()

    @property
    def quantity_max(self):
        """Max quantity."""
        return IArticleAdapter(self.context).quantity_max

    @property
    def soldout(self):
        return IArticleAdapter(self.context).soldout

    @property
    def available(self):
        return IArticleAdapter(self.context).addable_to_cart

    @property
    def uuid(self):
        return IUUID(self.context)


class AddSubArticleToCartViewlet(BaseAddToCartViewlet):
    """Viewlet to show add to cart form for subarticles."""
    grok.name('collective.cart.core.add-subarticle-to-cart')
    grok.template('add-subarticle-to-cart')

    @property
    def available(self):
        return IArticleAdapter(self.context).subarticle_addable_to_cart

    @property
    def soldout(self):
        return IArticleAdapter(self.context).subarticle_soldout

    @property
    def quantity_max(self):
        """Max quantity."""
        return IArticleAdapter(self.context).subarticle_quantity_max

    @property
    def subarticles(self):
        return IArticleAdapter(self.context).subarticles_option


class BelowArticleViewletManager(BaseViewletManager):
    """Viewlet manager which comes below article."""
    grok.context(IArticle)
    grok.name('collective.cart.shopping.below.article')


class ArticlesInArticleViewlet(BaseArticleViewlet):
    grok.name('collective.cart.shopping.articles.in.article')
    grok.template('articles-in-article')
    grok.viewletmanager(BelowArticleViewletManager)

    def articles(self):
        res = []
        for item in IContentListing(IArticleAdapter(self.context).articles_in_article):
            obj = item.getObject()
            article = IArticleAdapter(obj)
            addable_to_cart = article.addable_to_cart
            soldout = None
            quantity_max = 0
            if addable_to_cart:
                soldout = article.soldout
                quantity_max = article.quantity_max
            subarticle_addable_to_cart = article.subarticle_addable_to_cart
            if subarticle_addable_to_cart:
                soldout = article.subarticle_soldout
                quantity_max = article.subarticle_quantity_max
            numbers = xrange(1, quantity_max + 1)
            quantity_size = len(str(quantity_max))
            res.append({
                'addable_to_cart': addable_to_cart,
                'subarticle_addable_to_cart': subarticle_addable_to_cart,
                'description': item.Description(),
                'discount_end': article.discount_end,
                'gross': article.gross,
                'id': item.getId(),
                'image_url': article.image_url,
                'money': item.money,
                'numbers': numbers,
                'quantity_max': quantity_max,
                'quantity_size': quantity_size,
                'soldout': soldout,
                'subarticles': article.subarticles_option,
                'title': article.title,
                'url': item.getURL(),
                'uuid': item.uuid(),
                'vat': item.vat,
            })
        return res


class BaseCartArticlesViewlet(BaseBaseCartArticlesViewlet):
    """Base class for displaying articles in cart."""
    grok.baseclass()
    grok.layer(ICollectiveCartShoppingLayer)


class CartArticlesViewlet(BaseCartArticlesViewlet):
    """Cart Articles Viewlet Class."""

    def update(self):
        super(CartArticlesViewlet, self).update()
        form = self.request.form
        uuid = form.get('form.update.article', None)
        if uuid is not None:
            quantity = form.get('quantity', None)
            validate = validation.validatorFor('isInt')
            if quantity is not None and validate(quantity) == 1 and int(quantity) >= 0:
                quantity = int(quantity)
                shopping_site = self.view.shopping_site
                carticle = shopping_site.get_cart_article(uuid)
                adapter = getMultiAdapter((self.context, carticle), ICartArticleMultiAdapter)
                article = adapter.orig_article
                if quantity == 0:
                    shopping_site.remove_cart_articles(uuid)
                elif article:
                    stock = IStock(article).stock
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

            url = getMultiAdapter(
                (self.context, self.request), name='plone_context_state').current_base_url()
            return self.request.response.redirect(url)

    @property
    def articles(self):
        """Returns list of articles to show in cart."""
        res = []
        for article in super(CartArticlesViewlet, self).articles:
            adapter = getMultiAdapter((self.context, article), ICartArticleMultiAdapter)
            article.update({
                'gross_subtotal': adapter.gross_subtotal,
                'image_url': adapter.image_url,
                'quantity_max': adapter.quantity_max,
                'quantity_size': adapter.quantity_size,
            })
            res.append(article)
        return res


class BaseCartViewlet(BaseShoppingSiteRootViewlet):
    """Base viewlet for cart view."""
    grok.baseclass()
    grok.viewletmanager(CartViewletManager)


class CartTotalViewlet(BaseCartViewlet):
    """Viewlet to display total money of articles."""
    grok.name('collective.cart.shopping.cart-total')
    grok.template('cart-total')

    @property
    def cart_total(self):
        return IShoppingSite(self.context).articles_total


class CheckOutViewlet(BaseCartViewlet):
    """Viewlet to display check out buttons."""
    grok.name('collective.cart.shopping.checkout')
    grok.template('cart-checkout')

    def update(self):
        form = self.request.form
        if form.get('form.checkout') is not None:
            url = '{}/@@billing-and-shipping'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        if form.get('form.clear.cart') is not None:
            uuids = IShoppingSite(self.context).cart_articles.keys()
            IShoppingSite(self.context).remove_cart_articles(uuids)
            url = self.context.restrictedTraverse('plone_context_state').current_base_url()
            return self.request.response.redirect(url)


class BillingAndShippingViewletManager(BaseViewletManager):
    """Viewlet manager for billing and shipping page."""
    grok.name('collective.cart.shopping.billing.shipping.manager')


class BillingInfoViewlet(BaseShoppingSiteRootViewlet):
    """Viewlet class to show form to update billing address"""
    grok.name('collective.cart.shopping.billing.info')
    grok.template('billing-info')
    grok.viewletmanager(BillingAndShippingViewletManager)

    @property
    def billing_info(self):
        return IShoppingSite(self.context).get_info('billing')

    @property
    def shipping_methods(self):
        shopping_site = IShoppingSite(self.context)
        res = []
        for brain in shopping_site.shipping_methods:
            uuid = brain.UID
            orig_uuid = shopping_site.shipping_method['uuid']
            if uuid == orig_uuid:
                shipping_gross_money = shopping_site.shipping_gross_money
            else:
                shipping_gross_money = shopping_site.get_shipping_gross_money(uuid)
            res.append({
                'description': brain.Description,
                'checked': uuid == orig_uuid,
                'title': '{}  {} {}'.format(brain.Title, shipping_gross_money.amount, shipping_gross_money.currency),
                'uuid': uuid,
            })
        return res

    @property
    def single_shipping_method(self):
        return len(self.shipping_methods) == 1

    @property
    def billing_same_as_shipping(self):
        return IShoppingSite(self.context).cart.get('billing_same_as_shipping', True)

    def update(self):
        form = self.request.form
        shopping_site = IShoppingSite(self.context)
        shop_url = shopping_site.shop.absolute_url()
        if form.get('form.buttons.back') is not None:
            IShoppingSite(self.context).shop
            url = '{}/@@cart'.format(shop_url)
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
            shipping_method = form.get('shipping-method')
            if not self.single_shipping_method and not shipping_method:
                message = _('Select one shipping method.')
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

                billing = shopping_site.get_info('billing')
                if billing is None:
                    shopping_site.update_cart('billing', data)
                else:
                    for key in data:
                        if billing[key] != data[key]:
                            billing[key] = data[key]
                    shopping_site.update_cart('billing', billing)

                if form.get('billing-and-shipping-same-or-different') == 'same':
                    shopping_site.update_cart('billing_same_as_shipping', True)
                    url = '{}/@@order-confirmation'.format(shop_url)
                else:
                    shopping_site.update_cart('billing_same_as_shipping', False)
                    url = '{}/@@shipping-info'.format(shop_url)

                if shopping_site.shipping_method['uuid'] != shipping_method:
                    shopping_site.update_shipping_method(shipping_method)

                # notify(BillingAddressConfirmedEvent(cart))

                return self.request.response.redirect(url)


class OrderConfirmationViewletManager(BaseViewletManager):
    """Viewlet manager for order confirmation."""
    grok.name('collective.cart.shopping.order.confirmation.manager')


class BaseOrderConfirmationViewlet(BaseShoppingSiteRootViewlet):
    """Base class for viewlet in order-confirmation page."""
    grok.baseclass()
    grok.viewletmanager(OrderConfirmationViewletManager)


class OrderConfirmationCartArticlesViewlet(BaseOrderConfirmationViewlet, BaseCartArticlesViewlet):
    """Cart Articles Viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.confirmation-articles')
    grok.template('confirmation-cart-articles')

    @property
    def articles(self):
        """Returns list of articles to show in cart."""
        return IShoppingSite(self.context).cart_article_listing


class OrderConfirmationShippingMethodViewlet(BaseOrderConfirmationViewlet):
    """Shipping Method Viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.confirmation-shipping-method')
    grok.template('confirmation-shipping-method')

    @property
    def shipping_method(self):
        return IShoppingSite(self.context).shipping_method


class OrderConfirmationTotalViewlet(BaseOrderConfirmationViewlet):
    """Total Viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.confirmation-total')
    grok.template('confirmation-total')

    @property
    def total(self):
        return IShoppingSite(self.context).total


class TermsViewletManager(BaseViewletManager):
    """Viewlet manager for terms."""
    grok.name('collective.cart.shopping.terms.manager')


class OrderConfirmationTermsViewlet(BaseShoppingSiteRootViewlet, Message):
    """Viewlet to show terms for ordering..."""
    grok.name('confirmation-terms')
    grok.template('confirmation-terms')
    grok.viewletmanager(TermsViewletManager)


class OrderConfirmationCheckoutViewlet(BaseOrderConfirmationViewlet):
    """Check out viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.confirmation-checkout')
    grok.template('confirmation-checkout')


class CartContentViewlet(BaseCartContentViewlet):
    """Viewlet to show customer info in cart."""
    grok.layer(ICollectiveCartShoppingLayer)

    @property
    def order(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        cart = ICartAdapter(self.context)
        return {
            'articles': cart.articles,
            'id': self.context.id,
            'modified': cart.ulocalized_time(self.context.modified()),
            'shipping_method': cart.shipping_method,
            'state_title': workflow.getTitleForStateOnType(workflow.getInfoFor(self.context, 'review_state'), self.context.portal_type),
            'title': self.context.Title(),
            'total': cart.total,
            'url': self.context.absolute_url(),
            'billing_info': cart.get_address('billing'),
            'shipping_info': cart.get_address('shipping'),
        }


class CartContentDescriptionViewlet(BaseCartContentViewlet):
    """Viewlet to show description of cart."""
    grok.name('collective.cart.shopping.order.description')
    grok.template('cart-content-description')


class ArticleContainerViewletManager(BaseViewletManager):
    """Viewlet manager for ArticleContainer."""
    grok.context(IArticleContainer)
    grok.name('collective.cart.shopping.articlecontainer')


class BaseArticleContainerViewlet(BaseViewlet):
    """Base viewlet class for IArticleContainer"""
    grok.baseclass()
    grok.context(IArticleContainer)


class ArticlesInArticleContainerViewlet(BaseArticleContainerViewlet):
    """Viewlet to show Articles in ArticleContainer."""
    grok.name('collective.cart.core.articles-in-articlecontainer')
    grok.template('articles-in-articlecontainer')
    grok.viewletmanager(ArticleContainerViewletManager)

    @property
    def articles(self):
        res = []
        for item in IShoppingSite(self.context).get_content_listing(IArticle, depth=1, sort_on='getObjPositionInParent'):
            style_class = 'normal'
            obj = item.getObject()
            discount_available = IArticleAdapter(obj).discount_available
            if discount_available:
                style_class = 'discount'
            res.append({
                'discount-available': discount_available,
                'gross': IArticleAdapter(obj).gross,
                'money': item.money,
                'class': style_class,
                'title': item.Title(),
                'url': item.getURL(),
            })
        return res
