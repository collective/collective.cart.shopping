from Acquisition import aq_chain
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ATContentTypes.interfaces import IATImage
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from collective.base.interfaces import IAdapter
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.interfaces import IArticle
from collective.cart.shopping import _
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IArticleAddedToCartEvent
from collective.cart.shopping.interfaces import IOrder
from collective.cart.shopping.interfaces import IOrderAdapter
from collective.cart.shopping.interfaces import IShop
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IUnicodeUtility
from collective.cart.stock.interfaces import IStock as IStockContent
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

import logging


@adapter(IATImage, IObjectCreatedEvent)
def warn_number_of_images(context, event):
    if context == event.object:
        container = aq_chain(aq_inner(context))[3]
        if IArticle.providedBy(container):
            number_of_images = getUtility(IRegistry)['collective.cart.shopping.number_of_images']
            if len(IAdapter(container).get_brains(IATImage, depth=1)) >= number_of_images:
                message = _(u"You need to first remove some images to add here one.")
                IStatusMessage(container.REQUEST).addStatusMessage(message, type='warn')
                url = '{}/@@folder_contents'.format(container.absolute_url())
                return container.REQUEST.RESPONSE.redirect(url)


@adapter(IShop, IObjectAddedEvent)
def add_order_container_to_shop(obj, event):
    assert obj == event.object
    container = createContentInContainer(obj, 'collective.cart.core.OrderContainer',
        id="order-container", checkConstraints=False)
    modified(container)


@adapter(IShop, IObjectAddedEvent)
def add_shipping_method_container_to_shop(context, event):
    assert context == event.object
    container = createContentInContainer(context, 'collective.cart.shipping.ShippingMethodContainer',
        id='shipping-method-container', checkConstraints=False)
    modified(container)


@adapter(IOrder, IActionSucceededEvent)
def notify_ordered(context, event):
    if event.action == 'ordered':
        shopping_site = IShoppingSite(context)
        adapter = IOrderAdapter(context)
        portal = shopping_site.portal()
        email_from_address = getUtility(IRegistry)['collective.cart.shopping.notification_cc_email'] or portal.getProperty('email_from_address')

        billing = shopping_site.get_address('billing')
        default_charset = getattr(getattr(getToolByName(context, 'portal_properties'), 'site_properties'), 'default_charset', 'utf-8')
        email_charset = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        subject = context.translate(_(u'order-number', u'Order Number: ${number}', mapping={'number': context.id}))
        utility = getUtility(IUnicodeUtility)
        mfrom = u'"{}" <{}>'.format(utility.safe_unicode(shopping_site.shop().title), email_from_address)
        host = getToolByName(context, 'MailHost')

        underline = '=' * 28
        billing_address = utility.address(billing)
        if shopping_site.billing_same_as_shipping():
            shipping_address = billing_address
        else:
            shipping = shopping_site.get_address('shipping')
            shipping_address = utility.address(shipping)
        articles = shopping_site.cart_article_listing()
        for article in articles:
            subtotal = article['gross'] * article['quantity']
            article.update({'subtotal': shopping_site.format_money(subtotal)})
        shipping_method_title = hasattr(
            adapter.shipping_method(), 'Title') and adapter.shipping_method().Title.decode(default_charset) or u''

        items = shopping_site.cart().copy()
        for key in ['articles', 'billing_same_as_shipping', 'shipping_method', 'billing', 'shipping']:
            if key in items:
                del items[key]

        items.update({
            'number': context.id,
            'underline': underline,
            'billing_address': billing_address,
            'shipping_address': shipping_address,
            'articles': articles,
            'shipping_method_title': shipping_method_title,
            'is_shipping_free': shopping_site.shipping_gross_money().amount == 0.0,
            'shipping_gross': shopping_site.locale_shipping_gross(),
            'total': shopping_site.locale_total(),
        })

        message_to_customer = context.unrestrictedTraverse('@@to-customer-order-mail-template')(**items)
        mto_customer = u'"{}" <{}>'.format(utility.fullname(billing), billing['email'])
        subject_to_customer = subject

        message_to_shop = context.unrestrictedTraverse('@@to-shop-order-mail-template')(**items)
        mto_shop = mfrom
        subject_to_shop = subject

        try:
            host.send(message_to_customer, mto_customer, mfrom, subject=subject_to_customer, charset=email_charset)
            host.send(message_to_shop, mto_shop, mfrom, subject=subject_to_shop, charset=email_charset)

        except:
            message = _(u'order-processed-but',
                default=u'The order was processed but we could not send e-mail to you successfully. Please consult the shop owner.')
            IStatusMessage(context.REQUEST).addStatusMessage(message, type='warn')


@adapter(IArticleAddedToCartEvent)
def add_status_message_article_added(event):
    article = event.article
    message = _(u"article-added-to-cart", default=u"${title} is added to cart.", mapping={'title': safe_unicode(article.title())})
    IStatusMessage(event.request).addStatusMessage(message, type='info')


@adapter(IOrder, IActionSucceededEvent)
def return_stock_to_original_article(context, event):
    if event.action == 'canceled':
        adapter = IOrderAdapter(context)
        for article in adapter.articles():
            orig_article = adapter.get_object(IArticle, path=adapter.portal_path(), UID=article['id'])
            if orig_article:
                IStock(orig_article).add_stock(article['quantity'])
                modified(orig_article)


@adapter(IStockContent, IObjectAddedEvent)
def redirect_to_stock(context, event):
    if context == event.object:
        parent = aq_parent(aq_inner(context))
        url = '{}/@@stock'.format(parent.absolute_url())
        return context.REQUEST.RESPONSE.redirect(url)


@adapter(IArticle, IActionSucceededEvent)
def make_subarticles_private(context, event):
    """When article, which has subarticle(s), becomes private, all the subarticles must become private too."""
    action = event.action
    if (action == 'hide' or action == 'retract' or action == 'reject') and context.use_subarticle is True:
        adapter = IArticleAdapter(context)
        path = adapter.context_path()
        articles = adapter.get_objects(IArticle, path=path, review_state="published")
        wftool = getToolByName(context, 'portal_workflow')
        logger = logging.getLogger(__name__)
        for article in articles:
            article_path = '/'.join(article.getPhysicalPath())
            try:
                wftool.doActionFor(article, action)
                message = 'Also hidden subarticle: {}'.format(article_path)
                logger.info(message)
            except WorkflowException:
                message = 'Already hidden subarticle? {}'.format(article_path)
                logger.info(message)
