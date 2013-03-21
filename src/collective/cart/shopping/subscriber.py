from Acquisition import aq_chain
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ATContentTypes.interfaces import IATImage
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.interfaces import IArticle
from collective.cart.shopping import _
from collective.cart.shopping.interfaces import IArticleAddedToCartEvent
from collective.cart.shopping.interfaces import ICart
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICartArticleAdapter
from collective.cart.shopping.interfaces import IShop
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IUnicodeUtility
from collective.cart.stock.interfaces import IStock as IStockContent
from five import grok
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


def set_moneys(context):
    gross = context.money
    vat = gross * context.vat / (100 + context.vat)
    net = gross - vat
    setattr(context, 'vat_money', vat)
    setattr(context, 'net_money', net)
    discount_gross = IDiscount(context).discount_money
    if discount_gross:
        if not hasattr(context, 'discount_gross') or (
            hasattr(context, 'discount_gross') and context.discount_gross != discount_gross):
            discount_vat = discount_gross * context.vat / (100 + context.vat)
            discount_net = discount_gross - discount_vat
            setattr(context, 'discount_gross', discount_gross)
            setattr(context, 'discount_vat', discount_vat)
            setattr(context, 'discount_net', discount_net)


@grok.subscribe(IArticle, IObjectAddedEvent)
def create_moneys(context, event):
    set_moneys(context)


@grok.subscribe(IArticle, IObjectModifiedEvent)
def update_moneys(context, event):
    assert context == event.object
    set_moneys(context)


@grok.subscribe(IATImage, IObjectCreatedEvent)
def warn_number_of_images(context, event):
    if context == event.object:
        container = aq_chain(aq_inner(context))[3]
        if IArticle.providedBy(container):
            catalog = getToolByName(context, 'portal_catalog')
            query = {
                'path': {
                    'depth': 1,
                    'query': '/'.join(container.getPhysicalPath()),
                },
                'object_provides': IATImage.__identifier__,
            }
            number_of_images = getUtility(IRegistry)['collective.cart.shopping.number_of_images']
            if len(catalog(query)) >= number_of_images:
                message = _(u"You need to first remove some images to add here one.")
                IStatusMessage(container.REQUEST).addStatusMessage(message, type='warn')
                url = '{}/@@folder_contents'.format(container.absolute_url())
                return container.REQUEST.RESPONSE.redirect(url)


@grok.subscribe(IShop, IObjectAddedEvent)
def add_cart_container_to_shop(obj, event):
    assert obj == event.object
    container = createContentInContainer(obj, 'collective.cart.core.CartContainer',
        id="cart-container", title="Cart Container", checkConstraints=False)
    modified(container)


@grok.subscribe(IShop, IObjectAddedEvent)
def add_shipping_methods_to_shop(context, event):
    assert context == event.object
    container = createContentInContainer(context, 'collective.cart.shipping.ShippingMethodContainer',
        id='shipping-methods', title='Shipping Methods', checkConstraints=False)
    modified(container)


@grok.subscribe(ICart, IActionSucceededEvent)
def notify_ordered(context, event):
    if event.action == 'ordered':
        shopping_site = IShoppingSite(context)
        cadapter = ICartAdapter(context)
        portal = shopping_site.portal
        email_from_address = getUtility(IRegistry)['collective.cart.shopping.notification_cc_email'] or portal.getProperty('email_from_address')

        billing = shopping_site.get_address('billing')
        default_charset = getattr(getattr(getToolByName(context, 'portal_properties'), 'site_properties'), 'default_charset', 'utf-8')
        email_charset = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        subject = context.translate(_(u'order-number', u'Order Number: ${number}', mapping={'number': context.id}))
        utility = getUtility(IUnicodeUtility)
        mfrom = u'"{}" <{}>'.format(utility.safe_unicode(shopping_site.shop.title), email_from_address)
        host = getToolByName(context, 'MailHost')

        underline = '=' * 28
        billing_address = utility.address(billing)
        if shopping_site.billing_same_as_shipping:
            shipping_address = billing_address
        else:
            shipping = shopping_site.get_address('shipping')
            shipping_address = utility.address(shipping)
        articles = shopping_site.cart_article_listing
        for article in articles:
            subtotal = article['gross'] * article['quantity']
            article.update({'subtotal': shopping_site.format_money(subtotal)})
        shipping_method_title = hasattr(
            cadapter.shipping_method, 'Title') and cadapter.shipping_method.Title.decode(default_charset) or u''

        items = {
            'number': context.id,
            'underline': underline,
            'billing_address': billing_address,
            'shipping_address': shipping_address,
            'articles': articles,
            'shipping_method_title': shipping_method_title,
            'is_shipping_free': shopping_site.shipping_gross_money.amount == 0.0,
            'shipping_gross': shopping_site.locale_shipping_gross(),
            'total': shopping_site.locale_total(),
        }
        message_to_customer = context.unrestrictedTraverse('to-customer-order-mail-template')(**items)
        mto_customer = u'"{}" <{}>'.format(utility.fullname(billing), billing['email'])
        subject_to_customer = subject

        message_to_shop = context.unrestrictedTraverse('to-shop-order-mail-template')(**items)
        mto_shop = mfrom
        subject_to_shop = subject

        try:
            host.send(message_to_customer, mto_customer, mfrom, subject=subject_to_customer, charset=email_charset)
            host.send(message_to_shop, mto_shop, mfrom, subject=subject_to_shop, charset=email_charset)

        except:
            message = _(u'order-processed-but',
                default=u'The order was processed but we could not send e-mail to you successfully. Please consult the shop owner.')
            IStatusMessage(context.REQUEST).addStatusMessage(message, type='warn')


@grok.subscribe(IArticleAddedToCartEvent)
def status_message_article_added(event):
    article = event.article
    message = _(u"article-added-to-cart", default=u"${title} is added to cart.", mapping={'title': safe_unicode(article.title)})
    IStatusMessage(event.request).addStatusMessage(message, type='info')


@grok.subscribe(ICart, IActionSucceededEvent)
def return_stock_to_original(context, event):
    if event.action == 'canceled':
        for carticle in ICartAdapter(context).articles:
            obj = carticle['obj']
            article = ICartArticleAdapter(obj).orig_article
            if article:
                IStock(article).add_stock(obj.quantity)
                modified(article)


@grok.subscribe(IStockContent, IObjectAddedEvent)
def redirect_to_stock(context, event):
    if context == event.object:
        parent = aq_parent(aq_inner(context))
        url = '{}/@@stock'.format(parent.absolute_url())
        return context.REQUEST.RESPONSE.redirect(url)
