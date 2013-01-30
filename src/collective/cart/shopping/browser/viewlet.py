# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation import validation
from collective.behavior.stock.interfaces import IStock
from collective.cart import core
from collective.cart.core.browser.viewlet import CartContentViewletManager
from collective.cart.core.browser.viewlet import CartViewletManager
from collective.cart.core.interfaces import IBaseAdapter
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shipping.interfaces import IShippingMethod
from collective.cart.shopping import _
from collective.cart.shopping.browser.base import Message
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.event import BillingAddressConfirmedEvent
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import ICart
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICartArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IUpdateCart
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IBelowContent
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import modified


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


class BaseAddToCartViewlet(core.browser.viewlet.AddToCartViewlet):
    """Base class for add to cart viewlet."""
    grok.baseclass()
    grok.context(IArticle)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.viewletmanager(AddToCartViewletManager)

    def quantity_size(self):
        """Size for quantity field."""
        return len(str(self.quantity_max))


class AddToCartViewlet(BaseAddToCartViewlet):
    """Viewlet to show add to cart form for salable article.

    Can also add with certain number of quantity.
    """

    def update(self):
        getMultiAdapter((self.context, self.request), IUpdateCart).add_to_cart()

    @property
    def quantity_max(self):
        """Max quantity."""
        return IArticleAdapter(self.context).quantity_max

    @property
    def soldout(self):
        return IArticleAdapter(self.context).soldout

    def available(self):
        return IArticleAdapter(self.context).addable_to_cart

    def uuid(self):
        return IUUID(self.context)


class AddSubArticleToCartViewlet(BaseAddToCartViewlet):
    """Viewlet to show add to cart form for subarticles."""
    grok.name('collective.cart.core.add-subarticle-to-cart')
    grok.template('add-subarticle-to-cart')

    def available(self):
        return IArticleAdapter(self.context).subarticle_addable_to_cart

    @property
    def soldout(self):
        return IArticleAdapter(self.context).subarticle_soldout

    @property
    def quantity_max(self):
        """Max quantity."""
        return IArticleAdapter(self.context).subarticle_quantity_max

    def subarticles(self):
        return IArticleAdapter(self.context).subarticles_option


class BelowArticleViewletManager(BaseViewletManager):
    """Viewlet manager which comes below article."""
    grok.context(IArticle)
    grok.name('collective.cart.shopping.below.article')


class ArticlesInArticleViewlet(BaseArticleViewlet):
    grok.context(IArticle)
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


class BaseCartArticlesViewlet(core.browser.viewlet.CartArticlesViewlet):
    """Base class for displaying articles in cart."""
    grok.baseclass()
    grok.layer(ICollectiveCartShoppingLayer)


class CartArticlesViewlet(BaseCartArticlesViewlet):
    """Cart Articles Viewlet Class."""

    def update(self):
        super(CartArticlesViewlet, self).update()
        form = self.request.form
        oid = form.get('form.update.article', None)
        if oid is not None:
            quantity = form.get('quantity', None)
            if quantity is not None:
                try:
                    quantity = int(quantity)
                    shopping_site = IShoppingSite(self.context)
                    carticle = shopping_site.get_cart_article(oid)
                    article = ICartArticleAdapter(carticle).orig_article
                    if quantity == 0:
                        shopping_site.remove_cart_articles(oid)
                    elif quantity > carticle.quantity:
                        if article:
                            IStock(article).sub_stock(quantity - carticle.quantity)
                            carticle.quantity = quantity
                            modified(carticle)
                    elif quantity < carticle.quantity:
                        if article:
                            IStock(article).add_stock(carticle.quantity - quantity)
                        carticle.quantity = quantity
                        modified(carticle)
                except ValueError:
                    message = _(u"Invalid quantity.")
                    IStatusMessage(self.request).addStatusMessage(message, type='warn')
                    url = getMultiAdapter(
                        (self.context, self.request), name='plone_context_state').current_base_url()
                    self.request.response.redirect(url)
                return self.render()

    @property
    def articles(self):
        """Returns list of articles to show in cart."""
        cart = IShoppingSite(self.context).cart
        return ICartAdapter(cart).articles


class BaseCartViewlet(BaseShoppingSiteRootViewlet):
    """Base viewlet for cart view."""
    grok.baseclass()
    grok.viewletmanager(CartViewletManager)


class CartTotalViewlet(BaseCartViewlet):
    """Viewlet to display total money of articles."""
    grok.name('collective.cart.shopping.cart-total')
    grok.template('cart-total')

    def cart_total(self):
        return IShoppingSite(self.context).articles_total


class CheckOutViewlet(BaseCartViewlet):
    """Viewlet to display check out buttons."""
    grok.name('collective.cart.shopping.checkout')
    grok.template('cart-checkout')

    def update(self):
        form = self.request.form
        if form.get('form.checkout') is not None:
            cart = IShoppingSite(self.context).cart
            # Update shipping method.
            ICartAdapter(cart).update_shipping_method()
            url = '{}/@@billing-and-shipping'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        if form.get('form.clear.cart', None) is not None:
            ids = [item['id'] for item in IShoppingSite(self.context).cart_articles]
            IShoppingSite(self.context).remove_cart_articles(ids)
            url = getMultiAdapter(
                (self.context, self.request), name='plone_context_state').current_base_url()
            return self.request.response.redirect(url)


class BillingAndShippingViewletManager(BaseViewletManager):
    """Viewlet manager for billing and shipping page."""
    grok.name('collective.cart.shopping.billing.shipping.manager')


class BillingInfoViewlet(BaseShoppingSiteRootViewlet):
    """Viewlet class to show form to update billing address"""
    grok.name('collective.cart.shopping.billing.info')
    grok.template('billing-info')
    grok.viewletmanager(BillingAndShippingViewletManager)

    def billing_info(self):
        shopping_site = IShoppingSite(self.context)
        cart = shopping_site.cart
        billing = cart.get('billing')
        if billing:
            return {
                'first_name': billing.first_name,
                'last_name': billing.last_name,
                'organization': billing.organization,
                'vat': billing.vat,
                'email': billing.email,
                'street': billing.street,
                'post': billing.post,
                'city': billing.city,
                'phone': billing.phone,
            }
        else:
            return {
                'first_name': '',
                'last_name': '',
                'organization': '',
                'vat': '',
                'email': '',
                'street': '',
                'post': '',
                'city': '',
                'phone': '',
            }

    @property
    def shipping_methods(self):
        base = IBaseAdapter(self.context)
        brains = base.get_brains(IShippingMethod)
        shopping_site = IShoppingSite(self.context)
        cart = ICartAdapter(shopping_site.cart)
        res = []
        for brain in brains:
            uuid = brain.UID
            orig_uuid = cart.shipping_method.orig_uuid
            if uuid == orig_uuid:
                shipping_gross_money = cart.shipping_gross_money
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

    def billing_same_as_shipping(self):
        shopping_site = IShoppingSite(self.context)
        cart = shopping_site.cart
        return getattr(cart, 'billing_same_as_shipping', True)

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

                cart = shopping_site.cart

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

                billing = cart.get('billing')
                if billing is None:
                    billing = createContentInContainer(
                        cart, 'collective.cart.shopping.CustomerInfo', id='billing',
                        checkConstraints=False, **data)
                else:
                    for key in data:
                        if getattr(billing, key) != data[key]:
                            setattr(billing, key, data[key])

                modified(billing)

                if form.get('billing-and-shipping-same-or-different') == 'same':
                    cart.billing_same_as_shipping = True
                    url = '{}/@@order-confirmation'.format(shop_url)
                else:
                    cart.billing_same_as_shipping = False
                    url = '{}/@@shipping-info'.format(shop_url)

                cadapter = ICartAdapter(cart)
                if cadapter.shipping_method.orig_uuid != shipping_method:
                    cadapter.update_shipping_method(shipping_method)

                notify(BillingAddressConfirmedEvent(cart))

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

    def articles(self):
        """Returns list of articles to show in cart."""
        return ICartAdapter(self.view.cart).articles


class OrderConfirmationShippingMethodViewlet(BaseOrderConfirmationViewlet):
    """Shipping Method Viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.confirmation-shipping-method')
    grok.template('confirmation-shipping-method')

    def shipping_method(self):
        return ICartAdapter(self.view.cart).shipping_method


class OrderConfirmationTotalViewlet(BaseOrderConfirmationViewlet):
    """Total Viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.confirmation-total')
    grok.template('confirmation-total')

    def total(self):
        return ICartAdapter(self.view.cart).total


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

    def update(self):
        if self.request.form.get('form.buttons.back') is not None:
            portal_state = getMultiAdapter((self.context, self.request), name="plone_portal_state")
            url = '{}/@@cart'.format(portal_state.navigation_root_url())
            return self.request.response.redirect(url)


class BaseCartContentViewlet(BaseShoppingSiteRootViewlet):
    """Base class for viewlet within cart content."""
    grok.baseclass()
    grok.context(ICart)
    grok.viewletmanager(CartContentViewletManager)


class CustomerInfoViewlet(BaseCartContentViewlet):
    """Viewlet to show customer info in cart."""
    grok.name('collective.cart.core.customer-info')
    grok.template('customer-info')

    def billing(self):
        return self.context.get('billing')

    def shipping(self):
        return self.context.get('shipping')


class DescriptionCartContentViewlet(BaseCartContentViewlet):
    """Viewlet to show description of cart."""
    grok.name('collective.cart.shopping.cart-content-description')
    grok.template('cart-content-description')


class ShippingMethodCartContentViewlet(BaseCartContentViewlet):
    """Viewlet to show shipping method info in cart content."""
    grok.name('collective.cart.shopping.cart-content-shipping-method')
    grok.template('confirmation-shipping-method')

    def shipping_method(self):
        return ICartAdapter(self.context).shipping_method


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

    def articles(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        query = {
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'depth': 1,
            },
            'object_provides': IArticle.__identifier__,
            'sort_on': 'getObjPositionInParent',
        }
        res = []
        for item in IContentListing(catalog(query)):
            style_class = 'normal'
            discount_available = IArticleAdapter(item.getObject()).discount_available
            if discount_available:
                style_class = 'discount'
            res.append({
                'discount-available': discount_available,
                'gross': IArticleAdapter(item.getObject()).gross,
                'money': item.money,
                'class': style_class,
                'title': item.Title(),
                'url': item.getURL(),
            })
        return res
