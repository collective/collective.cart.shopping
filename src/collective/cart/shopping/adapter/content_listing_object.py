from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from plone.app.contentlisting.realobject import RealContentListingObject
from zope.component import adapts


class ArticleContentListingObject(RealContentListingObject):
    adapts(IArticle)

    def __init__(self, obj):
        super(ArticleContentListingObject, self).__init__(obj)
        self.adapter = IArticleAdapter(self._realobject)
        self.shopping_site = IShoppingSite(self._realobject)

    def __repr__(self):
        return "<collective.cart.shopping.adapter.content_listing_object.ArticleContentListingObject instance at {}>".format(self.getPath())

    def discount_available(self):
        """Return True if discount is available else False

        :rtype boolean
        """
        return self.adapter.discount_available()

    def klass(self):
        """Return discount if discount is available esle normal

        :rtype: str
        """
        if self.discount_available():
            return 'discount'
        else:
            return 'normal'

    def gross(self):
        """Reterun localized gross

        :rtype: unicode
        """
        return self.shopping_site.format_money(self.adapter.gross())

    def money(self):
        """Return localize money

        :rtype: unicode
        """
        return self.shopping_site.format_money(self._realobject.money)

# IContentListingObject

    def CroppedDescription(self):
        """A cropped description"""
        raise NotImplementedError

    def getSize(self):
        """size in bytes"""
        raise NotImplementedError
