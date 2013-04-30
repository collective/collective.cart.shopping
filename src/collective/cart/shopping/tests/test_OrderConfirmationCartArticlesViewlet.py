# from collective.cart.shopping.browser.viewlet import OrderConfirmationCartArticlesViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class OrderConfirmationCartArticlesViewletTestCase(IntegrationTestCase):
    """TestCase for OrderConfirmationCartArticlesViewlet"""

    def test(self):
        pass

    # def test_subclass(self):
    #     from collective.cart.shopping.browser.viewlet import BaseOrderConfirmationViewlet
    #     from collective.cart.shopping.browser.viewlet import BaseCartArticlesViewlet
    #     self.assertTrue(issubclass(OrderConfirmationCartArticlesViewlet,
    #         (BaseOrderConfirmationViewlet, BaseCartArticlesViewlet)))

    # def test_name(self):
    #     self.assertEqual(getattr(OrderConfirmationCartArticlesViewlet, 'grokcore.component.directive.name'),
    #         'collective.cart.shopping.confirmation-articles')

    # def test_template(self):
    #     self.assertEqual(getattr(OrderConfirmationCartArticlesViewlet, 'grokcore.view.directive.template'),
    #         'confirmation-cart-articles')

    # def test_articles(self):
    #     instance = self.create_viewlet(OrderConfirmationCartArticlesViewlet)
    #     self.assertEqual(len(instance.articles), 0)
