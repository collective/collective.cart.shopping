from collective.cart.shopping import _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


info_types = SimpleVocabulary([
    SimpleTerm(value=u'billing', title=_(u'Billing')), SimpleTerm(value=u'shipping', title=_(u'Shipping'))])
