from Acquisition import aq_inner
from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation import validation
from collective.behavior.stock.interfaces import IStock as IStockBehavior
from collective.cart import core
from collective.cart.core.interfaces import IBaseAdapter
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping import _
from collective.cart.shopping.browser.base import Message
from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
from collective.cart.shopping.event import ShippingAddressConfirmedEvent
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleContainer
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICustomerInfo
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.stock.interfaces import IStock
from five import grok
from plone.dexterity.utils import createContentInContainer
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import modified


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

    def title(self):
        return IArticleAdapter(self.context).title


class ArticleView(BaseArticleView):
    """Default view for Article."""
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


class StockView(BaseArticleView):
    """View to show and manage article's stock."""
    grok.name('stock')
    grok.require('cmf.ModifyPortalContent')
    grok.template('stock')

    @property
    def stock(self):
        return IStockBehavior(self.context).stock

    def stocks(self):
        plone = getMultiAdapter((self.context, self.request), name="plone")
        base = IBaseAdapter(self.context)
        res = []
        for item in base.get_content_listing(interface=IStock, depth=1, sort_on='created', sort_order='descending'):
            res.append({
                'crated': plone.toLocalizedTime(item.created),
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


class ShippingInfoView(BaseCheckoutView, Message):
    """View for editing shipping info which checkout"""
    grok.name('shipping-info')
    grok.template('shipping-info')

    def shipping_info(self):
        shopping_site = IShoppingSite(self.context)
        cart = shopping_site.cart
        return ICartAdapter(cart).get_info('shipping')

    def update(self):
        form = self.request.form
        shopping_site = IShoppingSite(self.context)
        shop_url = shopping_site.shop.absolute_url()
        if form.get('form.buttons.back') is not None:
            IShoppingSite(self.context).shop
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

                shipping = cart.get('shipping')
                if shipping is None:
                    shipping = createContentInContainer(
                        cart, 'collective.cart.shopping.CustomerInfo', id='shipping',
                        checkConstraints=False, **data)
                else:
                    for key in data:
                        if getattr(shipping, key) != data[key]:
                            setattr(shipping, key, data[key])

                modified(shipping)

                notify(ShippingAddressConfirmedEvent(cart))

                url = '{}/@@order-confirmation'.format(shop_url)
                return self.request.response.redirect(url)


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
        context_url = context.absolute_url()
        form = self.request.form
        if form.get('form.buttons.ConfirmOrder') is not None:
            if IShoppingSite(self.context).get_brain_for_text('confirmation-terms-message') and form.get('accept-terms') is None:
                message = _(u'need_to_accept_terms', default=u"You need to accept the terms to process the order.")
                IStatusMessage(self.request).addStatusMessage(message, type='info')
                url = '{}/@@order-confirmation'.format(context_url)
                return self.request.response.redirect(url)
            else:
                self.cart_id = self.cart.id
                workflow = getToolByName(context, 'portal_workflow')
                workflow.doActionFor(self.cart, 'ordered')

        elif form.get('form.buttons.back') is not None:
            url = '{}/@@billing-and-shipping'.format(context_url)
            return self.request.response.redirect(url)

        else:
            url = '{}/@@order-confirmation'.format(context_url)
            return self.request.response.redirect(url)

    def order_url(self):
        membership = getToolByName(self.context, 'portal_membership')
        return '{}?order_number={}'.format(membership.getHomeUrl(), self.cart_id)


class ArticleList(BaseView):
    """List for all the articles."""
    grok.context(IShoppingSiteRoot)
    grok.name('article-list')
    grok.require('cmf.ModifyPortalContent')
    grok.template('article-list')

    def articles(self):
        for item in IBaseAdapter(self.context).get_content_listing(interface=IArticle):
            obj = item.getObject()
            article = IArticleAdapter(obj)
            yield {
                'sku': item.sku,
                'stock': IStockBehavior(obj).stock,
                'title': article.title,
                'url': item.getURL(),
            }

    def update(self):
        self.request.set('disable_plone.leftcolumn', True)
        self.request.set('disable_plone.rightcolumn', True)


class CustomerInfoView(BaseView):
    """View for Customer Info."""
    grok.context(ICustomerInfo)
    grok.name('view')
    grok.template('customer-info')
