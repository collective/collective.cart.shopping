from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.ATContentTypes.interfaces import IATImage
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.stock.interfaces import IStock
from collective.cart.core.interfaces import ICartArticle
from collective.cart.core.interfaces import ICartArticleAdapter
from collective.cart.core.interfaces import IMakeShoppingSiteEvent
from collective.cart.shopping import _
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IShop
from five import grok
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
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


@grok.subscribe(IArticle, IObjectCreatedEvent)
def create_moneys(context, event):
    assert context == event.object
    set_moneys(context)


@grok.subscribe(IArticle, IObjectModifiedEvent)
def update_moneys(context, event):
    assert context == event.object
    set_moneys(context)


@grok.subscribe(ICartArticle, IObjectRemovedEvent)
def set_quantity_back_to_orig_article(context, event):
    assert context == event.object
    article = ICartArticleAdapter(context).orig_article
    IStock(article).add_stock(context.quantity)
    modified(article)


@grok.subscribe(IATImage, IObjectCreatedEvent)
def warn_number_of_images(context, event):
    assert context == event.object
    container = aq_chain(aq_inner(context))[3]
    if IArticle.providedBy(container):
        catalog = getToolByName(context, 'portal_catalog')
        query = {
            'path': {
                'depth': 1,
                'query': '/'.join(container.getPhysicalPath()),
            }
        }
        number_of_images = getUtility(IRegistry)['collective.cart.shopping.number_of_images']
        if len(catalog(query)) >= number_of_images:
            message = _(u"You need to first remove some images to add here one.")
            IStatusMessage(container.REQUEST).addStatusMessage(message, type='warn')
            url = '{}/@@folder_contents'.format(container.absolute_url())
            return container.REQUEST.RESPONSE.redirect(url)


@grok.subscribe(IMakeShoppingSiteEvent)
def add_shopping_methods(event):
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
def add_shopping_methods_to_shop(context, event):
    assert context == event.object
    container = createContentInContainer(context, 'collective.cart.shipping.ShippingMethodContainer',
        id='shipping-methods', title='Shipping Methods', checkConstraints=False)
    modified(container)
