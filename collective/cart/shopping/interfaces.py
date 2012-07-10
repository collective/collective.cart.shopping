from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IArticleAdapter
from collective.cart.shopping import _
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage
from zope.interface import Attribute


class IArticle(IArticle, IImageScaleTraversable):

    image = NamedBlobImage(
        title=_('Representative Image'),
        description=_('The representative image of this article.'),
        required=False)


class IArticleAdapter(IArticleAdapter):

    gross = Attribute('Gross money for the article.')
    vat = Attribute('VAT money for the article.')
    net = Attribute('Net money for the article.')
    soldout = Attribute('True or False for soldout.')
