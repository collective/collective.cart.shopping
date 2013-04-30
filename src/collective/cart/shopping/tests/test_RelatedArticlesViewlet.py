from collective.cart.shopping.tests.base import IntegrationTestCase
from collective.cart.shopping.browser.viewlet import RelatedArticlesViewlet


class RelatedArticlesViewletTestCase(IntegrationTestCase):
    """TestCase for RelatedArticlesViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(RelatedArticlesViewlet, ViewletBase))

    def test_index(self):
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(RelatedArticlesViewlet, context)
        self.assertEqual(instance.index.filename.split('/')[-1], 'related-articles.pt')
