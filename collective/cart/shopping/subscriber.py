from collective.behavior.discount.interfaces import IDiscount
from collective.behavior.stock.interfaces import IStock
from collective.cart.shopping.interfaces import IArticle
from collective.cart.core.interfaces import ICartArticle
from collective.cart.core.interfaces import ICartArticleAdapter
from five import grok
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent import modified


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
