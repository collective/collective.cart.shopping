from collective.cart.shipping.interfaces import IShippingMethod
from collective.cart.core.interfaces import IBaseAdapter
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from five import grok
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class ShippingMethodsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        base = IBaseAdapter(context)
        brains = base.get_brains(IShippingMethod)
        cart = ICartAdapter(IShoppingSite(context).cart)
        shopping_site = IShoppingSite(context)
        terms = []
        for brain in brains:
            uuid = brain.UID
            if uuid == cart.shipping_method.orig_uuid:
                shipping_gross_money = cart.shipping_gross_money
            else:
                shipping_gross_money = shopping_site.get_shipping_gross_money(uuid)
            terms.append(SimpleVocabulary.createTerm(brain.UID, brain.UID,
                '{}  {} {}'.format(brain.Title, shipping_gross_money.amount, shipping_gross_money.currency)))

        return SimpleVocabulary(terms)


grok.global_utility(ShippingMethodsVocabulary, name=u"collective.cart.shipping.methods")
