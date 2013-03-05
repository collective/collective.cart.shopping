from collective.cart.shopping.browser.viewlet import OrderConfirmationCartArticlesViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest

import mock


class OrderConfirmationCartArticlesViewletTestCase(IntegrationTestCase):
    """TestCase for OrderConfirmationCartArticlesViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseOrderConfirmationViewlet
        from collective.cart.shopping.browser.viewlet import BaseCartArticlesViewlet
        self.assertTrue(issubclass(OrderConfirmationCartArticlesViewlet,
            (BaseOrderConfirmationViewlet, BaseCartArticlesViewlet)))

    def test_name(self):
        self.assertEqual(getattr(OrderConfirmationCartArticlesViewlet, 'grokcore.component.directive.name'),
            'collective.cart.shopping.confirmation-articles')

    def test_template(self):
        self.assertEqual(getattr(OrderConfirmationCartArticlesViewlet, 'grokcore.view.directive.template'),
            'confirmation-cart-articles')

    def create_viewlet(self):
        context = mock.Mock()
        request = TestRequest()
        return OrderConfirmationCartArticlesViewlet(context, request, None, None)

    @mock.patch('collective.cart.shopping.browser.viewlet.IShoppingSite')
    def test_articles(self, IShoppingSite):
        instance = self.create_viewlet()
        self.assertEqual(instance.articles, IShoppingSite().cart_article_listing)
