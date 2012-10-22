from Products.CMFCore.utils import getToolByName
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.dexterity.utils import createContentInContainer
from zope.lifecycleevent import modified

class TestCase(IntegrationTestCase):
    """TestCase for ArticleAdapter."""

    def setUp(self):
        self.portal = self.layer['portal']

    def create_article(self):
        article = createContentInContainer(
            self.portal, 'collective.cart.core.Article',
            checkConstraints=False, title='Article', sku='SKU1', money=12.3, vat=23.0)
        modified(article)
        return article

    def create_subarticle(self, parent):
        subarticle = createContentInContainer(
            parent, 'collective.cart.shopping.SubArticle',
            checkConstraints=False, title='Subarticle', sku='SKU2', money=24.6, vat=13.0)
        modified(subarticle)
        return subarticle

    def create_stock(self, parent, stock):
        import pdb; pdb.set_trace()
        item = createContentInContainer(
            parent, 'collective.cart.stock.Stock', id='stock',
            checkConstraints=False, title='Stock', stock=stock)
        modified(item)
        return item


    def test_subarticles__zero(self):
        from collective.cart.shopping.interfaces import IArticleAdapter
        article = self.create_article()
        self.assertEqual(len(IArticleAdapter(article).subarticles), 0)

    def test_subarticles(self):
        from collective.cart.shopping.interfaces import IArticleAdapter
        article = self.create_article()
        subarticle = self.create_subarticle(article)
        self.assertEqual(len(IArticleAdapter(article).subarticles), 0)

        # Turn use_subarticle on.
        article.use_subarticle = True
        modified(article)
        self.assertEqual(len(IArticleAdapter(article).subarticles), 0)
