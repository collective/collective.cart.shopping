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
from collective.cart.core.interfaces import ICartArticle
from collective.cart.core.interfaces import IMakeShoppingSiteEvent
from collective.cart.shopping import _
from collective.cart.shopping.interfaces import IArticleAddedToCartEvent
from collective.cart.shopping.interfaces import ICart
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICartArticleAdapter
from collective.cart.shopping.interfaces import IShop
from collective.cart.stock.interfaces import IStock as IStockContent
from email import message_from_string
from email.Header import Header
from five import grok
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from smtplib import SMTPRecipientsRefused
from zope.component import getUtility
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


def set_moneys(context):
    if not hasattr(context, 'gross_money') or (
        hasattr(context, 'gross_money') and context.gross_money != context.money):
        gross = context.money
        vat = gross * context.vat / (100 + context.vat)
        net = gross - vat
        setattr(context, 'gross_money', gross)
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


@grok.subscribe(ICartArticle, IObjectRemovedEvent)
def set_quantity_back_to_orig_article(context, event):
    article = ICartArticleAdapter(context).orig_article
    if article:
        IStock(article).add_stock(context.quantity)
        modified(article)


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


@grok.subscribe(IMakeShoppingSiteEvent)
def add_shipping_methods(event):
    context = event.context
    if not context.get('shipping-methods'):
        folder = context[context.invokeFactory('Folder', 'shipping-methods', title='Shipping Methods')]
        folder.setExcludeFromNav(True)
        folder.reindexObject()


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
        portal = getToolByName(context, 'portal_url').getPortalObject()
        email_from_address = getUtility(IRegistry)['collective.cart.shopping.notification_cc_email'] or portal.getProperty('email_from_address')
        # email_from_name = portal.getProperty('email_from_name')

        cadapter = ICartAdapter(context)
        billing_info = cadapter.get_address('billing')
        email_to_address = billing_info.email
        # email_to_name = u'{} {}'.format(billing_info.first_name, billing_info.last_name)
        default_charset = getattr(getattr(getToolByName(context, 'portal_properties'), 'site_properties'), 'default_charset', 'utf-8')
        encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        subject = context.translate(_(u'Ordered'))
        mto = email_to_address
        mfrom = email_from_address
        host = getToolByName(context, 'MailHost')

        # First message
        FIRST_MESSAGE = context.translate(_(u'Thank you for the order.'))

        # Order number
        ORDER_NUMBER = context.translate(_(u'order-number', u'Order Number: ${number}', mapping={'number': context.id}))

        # Billing address
        BILLING_ADDRESS = context.translate(_(u'Billing Address'))
        BILLING_INFO = u"""{first_name} {last_name}  {organization}  {vat}
{street}
{post} {city}
{phone}
{email}
""".format(
            first_name=safe_unicode(billing_info.first_name, encoding=default_charset),
            last_name=safe_unicode(billing_info.last_name, encoding=default_charset),
            organization=safe_unicode(billing_info.organization, encoding=default_charset),
            vat=safe_unicode(billing_info.vat, encoding=default_charset),
            street=safe_unicode(billing_info.street, encoding=default_charset),
            post=safe_unicode(billing_info.post, encoding=default_charset),
            city=safe_unicode(billing_info.city, encoding=default_charset),
            phone=safe_unicode(billing_info.phone, encoding=default_charset),
            email=billing_info.email)

        # Shipping address
        if context.billing_same_as_shipping:
            shipping_info = billing_info
        else:
            shipping_info = cadapter.get_address('shipping')
        SHIPPING_ADDRESS = context.translate(_(u'Shipping Address'))
        SHIPPING_INFO = u"""{first_name} {last_name}  {organization}  {vat}
{street}
{post} {city}
{phone}
{email}
""".format(
            first_name=safe_unicode(shipping_info.first_name, encoding=default_charset),
            last_name=safe_unicode(shipping_info.last_name, encoding=default_charset),
            organization=safe_unicode(shipping_info.organization, encoding=default_charset),
            vat=safe_unicode(shipping_info.vat, encoding=default_charset),
            street=safe_unicode(shipping_info.street, encoding=default_charset),
            post=safe_unicode(shipping_info.post, encoding=default_charset),
            city=safe_unicode(shipping_info.city, encoding=default_charset),
            phone=safe_unicode(shipping_info.phone, encoding=default_charset),
            email=shipping_info.email)

        # Ordered contents
        ORDERED_CONTENTS = context.translate(_(u'Ordered contents'))
        SKU = context.translate(_(u'SKU'))
        articles = []
        for article in cadapter.articles:
            article_line = u'{SKU}: {sku}\n{title} x {quantity} = {subtotal}'.format(
                SKU=SKU,
                sku=article['sku'],
                title=article['title'],
                quantity=article['quantity'],
                subtotal=article['gross_subtotal'])
            articles.append(article_line)
        article_lines = u'\n'.join(articles)

        SHIPPING_METHOD = context.translate(_(u'Shipping Method'))
        shipping_method = hasattr(
            cadapter.shipping_method, 'Title') and cadapter.shipping_method.Title.decode(encoding) or u''

        TOTAL = context.translate(_(u'Total'))

        # Link to the order
        url = context.absolute_url()
        LINK = context.translate(_(u'link-to-order', u'Link to the order: ${url}', mapping={'url': url}))

        mail_text = u"""{FIRST_MESSAGE}

{ORDER_NUMBER}

{BILLING_ADDRESS}
{underline}
{BILLING_INFO}

{SHIPPING_ADDRESS}
{underline}
{SHIPPING_INFO}

{ORDERED_CONTENTS}
{underline}
{article_lines}

{SHIPPING_METHOD}: {shipping_method}  {shipping_gross_momey}

{TOTAL}: {total}

{LINK}""".format(
            FIRST_MESSAGE=FIRST_MESSAGE,
            ORDER_NUMBER=ORDER_NUMBER,
            BILLING_ADDRESS=BILLING_ADDRESS,
            BILLING_INFO=BILLING_INFO,
            SHIPPING_ADDRESS=SHIPPING_ADDRESS,
            SHIPPING_INFO=SHIPPING_INFO,
            ORDERED_CONTENTS=ORDERED_CONTENTS,
            article_lines=article_lines,
            underline='=' * 28,
            SHIPPING_METHOD=SHIPPING_METHOD,
            shipping_method=shipping_method,
            shipping_gross_momey=cadapter.shipping_gross_money,
            TOTAL=TOTAL,
            total=cadapter.total,
            LINK=LINK)

        message = message_from_string(mail_text.encode(encoding).strip())
        message.set_charset(encoding)
        message['CC'] = Header(mfrom)

        try:
            host.send(message, mto, mfrom, subject=subject,
                      charset=encoding)
        except SMTPRecipientsRefused:
            # Don't disclose email address on failure
            raise SMTPRecipientsRefused(
                _(u'Recipient address rejected by server.'))


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
