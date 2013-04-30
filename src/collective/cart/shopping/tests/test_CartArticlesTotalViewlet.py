from collective.cart.shopping.browser.viewlet import CartArticlesTotalViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class CartArticlesTotalViewletTestCase(IntegrationTestCase):
    """TestCase for CartArticlesTotalViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(CartArticlesTotalViewlet, ViewletBase))

    def test_index(self):
        instance = self.create_viewlet(CartArticlesTotalViewlet)
        self.assertEqual(instance.index.filename.split('/')[-1], 'cart-articles-total.pt')

    # @mock.patch('collective.cart.shopping.browser.viewlet.IShoppingSite')
    # def test_articles_total(self, IShoppingSite):
    #     instance = self.create_viewlet(CartArticlesTotalViewlet)
    #     self.assertEqual(instance.articles_total(), IShoppingSite().format_money())
