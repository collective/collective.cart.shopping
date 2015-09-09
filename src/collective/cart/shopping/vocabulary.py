from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from plone.uuid.interfaces import IUUID
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class RelatedArticlesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        res = []
        adapter = IShoppingSite(context)
        path = adapter.shop_path()
        for item in adapter.get_content_listing(IArticle, path=path):
            obj = item.getObject()
            uuid = IUUID(obj)
            if not IPloneSiteRoot.providedBy(context) and uuid != IUUID(context):
                res.append((IArticleAdapter(obj).title(), uuid))
        res.sort()
        terms = [SimpleTerm(item[1], item[1], item[0]) for item in res]

        return SimpleVocabulary(terms)


RelatedArticlesVocabularyFactory = RelatedArticlesVocabulary()
