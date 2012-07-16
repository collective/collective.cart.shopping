from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IArticleAdapter
from collective.cart.shopping import _
from plone.app.textfield import RichText
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import Attribute
from zope.schema import TextLine
from zope.interface import Interface


class IArticle(IArticle, IImageScaleTraversable):

    image = NamedBlobImage(
        title=_(u'Representative Image'),
        description=_(u'The representative image of this article.'),
        required=False)

    text = RichText(
        title=_(u'Detailed information'),
        description=_(u'Further detailed information comes here.'),
        required=False)

class IArticleAdapter(IArticleAdapter):

    gross = Attribute('Gross money for the article.')
    vat = Attribute('VAT money for the article.')
    net = Attribute('Net money for the article.')
    soldout = Attribute('True or False for sold out.')


# class IInfoSchema(form.Schema):
class IInfoSchema(Interface):
    """Billing and Shipping related schema."""

    name = TextLine(
        title=_(u'Name'))

    title = TextLine(title=u"Title")