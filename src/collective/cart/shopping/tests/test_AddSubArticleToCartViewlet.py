from collective.cart.shopping.browser.viewlet import AddSubArticleToCartViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest

import mock


class AddSubArticleToCartViewletTestCase(IntegrationTestCase):
    """TestCase for AddSubArticleToCartViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseAddToCartViewlet
        self.assertTrue(issubclass(AddSubArticleToCartViewlet, BaseAddToCartViewlet))

    def test_name(self):
        self.assertEqual(getattr(AddSubArticleToCartViewlet, 'grokcore.component.directive.name'), 'collective.cart.core.add-subarticle-to-cart')

    def test_template(self):
        self.assertEqual(getattr(AddSubArticleToCartViewlet, 'grokcore.view.directive.template'), 'add-subarticle-to-cart')

    def create_viewlet(self):
        context = mock.Mock()
        request = TestRequest()
        return AddSubArticleToCartViewlet(context, request, None, None)

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_available(self, IArticleAdapter):
        instance = self.create_viewlet()
        IArticleAdapter().subarticle_addable_to_cart = True
        self.assertTrue(instance.available)

        IArticleAdapter().subarticle_addable_to_cart = False
        self.assertFalse(instance.available)

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_soldout(self, IArticleAdapter):
        instance = self.create_viewlet()
        IArticleAdapter().subarticle_soldout = True
        self.assertTrue(instance.soldout)

        IArticleAdapter().subarticle_soldout = False
        self.assertFalse(instance.soldout)

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_quantity_max(self, IArticleAdapter):
        instance = self.create_viewlet()
        IArticleAdapter().subarticle_quantity_max = 10
        self.assertEqual(instance.quantity_max, 10)

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_subarticles(self, IArticleAdapter):
        instance = self.create_viewlet()
        IArticleAdapter().subarticles_option = 'SUBARTICLES'
        self.assertEqual(instance.subarticles, 'SUBARTICLES')
