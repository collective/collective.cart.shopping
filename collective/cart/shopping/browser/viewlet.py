from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from collective.behavior.size.interfaces import ISize
from collective.behavior.stock.interfaces import IStock
from collective.cart import core
from collective.cart import shipping
from collective.cart.core.browser.viewlet import CartContentViewletManager
from collective.cart.core.browser.viewlet import CartViewletManager
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping import _
from collective.cart.shopping.browser.form import BillingInfoForm
from collective.cart.shopping.browser.form import ShippingInfoForm
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.browser.wrapper import ShippingMethodFormWrapper
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import ICart
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICartArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.z3cform.layout import FormWrapper
from zope.component import getMultiAdapter
from zope.interface import Interface
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
    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartShoppingLayer)
    grok.require('zope2.View')


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


class AddToCartViewlet(BaseAddToCartViewlet):
    """Viewlet to show add to cart form for salable article.

    Can also add with certain number of quantity.
    """

    def update(self):
        form = self.request.form
        if form.get('form.addtocart', None) is not None:
            quantity = form.get('quantity', None)
            if quantity is not None and IArticleAdapter(self.context).addable_to_cart:
                url = getMultiAdapter(
                    (self.context, self.request), name='plone_context_state').current_base_url()
                try:
                    quantity = int(quantity)
                    if quantity > IArticleAdapter(self.context).quantity_max:
                        quantity = IArticleAdapter(self.context).quantity_max
                    item = IArticleAdapter(self.context)
                    kwargs = {
                        'gross': item.gross,
                        'net': item.net,
                        'vat': item.vat,
                        'vat_rate': item.context.vat,
                        'quantity': quantity,
                        'weight': ISize(self.context).weight,
                        'width': ISize(self.context).width,
                        'height': ISize(self.context).height,
                        'depth': ISize(self.context).depth,
                    }
                    IArticleAdapter(self.context).add_to_cart(**kwargs)
                    IStock(self.context).sub_stock(quantity)
                    return self.request.response.redirect(url)
                except ValueError:
                    message = _(u"Input integer value to add to cart.")
                    IStatusMessage(self.request).addStatusMessage(message, type='warn')
                    return self.request.response.redirect(url)

    @property
    def quantity_max(self):
        """Max quantity."""
        return IArticleAdapter(self.context).quantity_max

    def quantity_size(self):
        """Size for quantity field."""
        return len(str(self.quantity_max))

    def numbers(self):
        """Iterable all numbers."""
        return xrange(1, self.quantity_max + 1)

    @property
    def soldout(self):
        return IArticleAdapter(self.context).soldout

    def available(self):
        return IArticleAdapter(self.context).addable_to_cart


class AddSubArticleToCartViewlet(AddToCartViewlet):
    """Viewlet to show add to cart form for subarticles."""
    grok.name('collective.cart.core.add-subarticle-to-cart')
    grok.template('add-subarticle-to-cart')

    def update(self):
        form = self.request.form

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
        return IArticleAdapter(self.context).subarticles


class BaseCartArticlesViewlet(core.browser.viewlet.CartArticlesViewlet):
    """Base class for displaying articles in cart."""
    grok.baseclass()
    grok.layer(ICollectiveCartShoppingLayer)

    def _image(self, obj):
        scales = getMultiAdapter((obj, self.request), name='images')
        scale = scales.scale('image', scale='thumb')
        if scale:
            return scale.tag()


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
                    carticle = IShoppingSite(self.context).get_cart_article(oid)
                    article = ICartArticleAdapter(carticle).orig_article
                    if quantity > carticle.quantity:
                        if article:
                            IStock(article).sub_stock(quantity - carticle.quantity)
                            carticle.quantity = quantity
                            modified(carticle)
                    if quantity < carticle.quantity:
                        if article:
                            IStock(article).add_stock(carticle.quantity - quantity)
                        carticle.quantity = quantity
                        modified(carticle)
                except ValueError:
                    message = _(u"Input integer value to update cart.")
                    IStatusMessage(self.request).addStatusMessage(message, type='warn')
                return self.render()

    @property
    def articles(self):
        """Returns list of articles to show in cart."""
        results = []
        for item in IContentListing(self.view.cart_articles):
            obj = item.getObject()
            items = self._items(item)
            items['image'] = None
            items['description'] = None
            items['gross'] = obj.gross
            quantity = obj.quantity
            items['quantity'] = quantity
            items['vat_rate'] = obj.vat_rate
            quantity_max = quantity
            orig_article = ICartArticleAdapter(obj).orig_article
            if orig_article:
                items['image'] = self._image(orig_article)
                items['description'] = orig_article.Description()
                quantity_max += IStock(orig_article).stock
            items['quantity_max'] = quantity_max
            items['quantity_size'] = len(str(quantity_max))
            items['numbers'] = xrange(1, quantity_max + 1)
            results.append(items)
        return results


class BaseCartViewlet(BaseViewlet):
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
        if form.get('form.checkout', None) is not None:
            cart = IShoppingSite(self.context).cart
            # Update shipping method.
            ICartAdapter(cart).update_shipping_method()
            url = '{}/@@billing-and-shipping'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        if form.get('form.clear.cart', None) is not None:
            ids = [brain.id for brain in IShoppingSite(self.context).cart_articles]
            IShoppingSite(self.context).remove_cart_articles(ids)
            url = getMultiAdapter(
                (self.context, self.request), name='plone_context_state').current_base_url()
            return self.request.response.redirect(url)


class BillingAndShippingViewletManager(BaseViewletManager):
    """Viewlet manager for billing and shipping page."""
    grok.name('collective.cart.shopping.billing.shipping.manager')


class BaseCustomerInfoViewlet(BaseViewlet):
    grok.baseclass()
    grok.viewletmanager(BillingAndShippingViewletManager)

    def create_form(self, form_class):
        view = FormWrapper(self.context, self.request)
        form = form_class(self.context, self.request)
        view.form_instance = form
        return view()


class FormWrapper(FormWrapper):

    index = ViewPageTemplateFile('viewlets/formwrapper.pt')


class BillingInfoViewlet(BaseCustomerInfoViewlet):
    grok.name('collective.cart.shopping.billing.info')
    grok.template('info')

    title = _('Billing Info')

    def form(self):
        return self.create_form(BillingInfoForm)


class ShippingInfoViewlet(BaseCustomerInfoViewlet):
    grok.name('collective.cart.shopping.shipping.info')
    grok.template('info')

    title = _('Shipping Info')

    def form(self):
        return self.create_form(ShippingInfoForm)


class ShippingMethodViewlet(BaseCustomerInfoViewlet, shipping.browser.viewlet.ShippingMethodViewlet):
    grok.view(Interface)

    _form_wrapper = ShippingMethodFormWrapper


class BillingShippingCheckOutViewlet(BaseCustomerInfoViewlet):
    grok.name('collective.cart.shopping.billing.shipping.method.checkout')
    grok.template('billing-and-shipping-checkout')

    def action_url(self):
        return '{}/@@order-confirmation'.format(self.context.absolute_url())

    def cart_id(self):
        return IShoppingSite(self.context).cart.id


class OrderConfirmationViewletManager(BaseViewletManager):
    """Viewlet manager for order confirmation."""
    grok.name('collective.cart.shopping.order.confirmation.manager')


class BaseOrderConfirmationViewlet(BaseViewlet):
    """Base class for viewlet in order-confirmation page."""
    grok.baseclass()
    grok.viewletmanager(OrderConfirmationViewletManager)

    def cart(self, cid=None):
        """Cart object."""
        container = IShoppingSite(self.context).cart_container
        if container and cid is None:
            cid = self.view.cart_id
        return container.get(cid)


class OrderConfirmationCartArticlesViewlet(BaseOrderConfirmationViewlet, BaseCartArticlesViewlet):
    """Cart Articles Viewlet for OrderConfirmationViewletManager."""
    grok.template('confirmation-cart-articles')

    @property
    def cart_articles(self):
        """List of CartArticles within cart."""
        cart = self.cart()
        if cart:
            return ICartAdapter(cart).articles

    @property
    def articles(self):
        """Returns list of articles to show in cart."""
        results = []
        for item in IContentListing(self.cart_articles):
            obj = item.getObject()
            items = self._items(item)
            items['image'] = None
            items['description'] = None
            items['vat_rate'] = obj.vat_rate
            items['gross_subtotal'] = ICartArticleAdapter(obj).gross_subtotal
            orig_article = ICartArticleAdapter(obj).orig_article
            if orig_article:
                items['image'] = self._image(orig_article)
                items['description'] = orig_article.Description()
            results.append(items)
        return results


class OrderConfirmationShippingMethodViewlet(BaseOrderConfirmationViewlet):
    """Shipping Method Viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.confirmation-shipping-method')
    grok.template('confirmation-shipping-method')

    def shipping_method(self):
        cart = self.cart()
        if cart:
            return ICartAdapter(cart).shipping_method


class OrderConfirmationTotalViewlet(BaseOrderConfirmationViewlet):
    """Total Viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.confirmation-total')
    grok.template('confirmation-total')

    def total(self):
        cart = self.cart()
        if cart:
            return ICartAdapter(cart).total


class OrderConfirmationViewOrderViewlet(BaseOrderConfirmationViewlet):
    """View Order Viewlet for OrderConfirmationViewletManager."""
    grok.name('collective.cart.shopping.cofirmation-view-order')
    grok.template('confirmation-view-order')

    def cart_url(self):
        cart = self.cart()
        if cart:
            return cart.absolute_url()


class BaseCartContentViewlet(BaseViewlet):
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


class ArticlesInArticleContainerViewlet(BaseViewlet):
    """Viewlet to show Articles in ArticleContainer."""
    grok.context(IArticleContainer)
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
        return [{
            # 'image': self._image(item),
            'discount-available': IArticleAdapter(item.getObject()).discount_available,
            'gross': IArticleAdapter(item.getObject()).gross,
            'money': item.money,
            'style': 'style',
            'title': item.Title(),
            'url': item.getURL(),
        } for item in IContentListing(catalog(query))]

    # def _image(self, item):
    #     """Returns scales image tag."""
    #     scales = getMultiAdapter((item.getObject(), self.request), name='images')
    #     scale = scales.scale('image', scale='thumb')
    #     if scale:
    #         return scale.tag()
    #     else:
    #         portal_state = getMultiAdapter(
    #             (self.context, self.request), name=u'plone_portal_state')
    #         image_url = '{0}/++theme++sll.theme/images/feed-fallback.png'.format(
    #             portal_state.portal_url())
    #         return u'<img src="{0}" alt="{1}" title="{1}" width="128" />'.format(
    #             image_url,
    #             item.Title())
