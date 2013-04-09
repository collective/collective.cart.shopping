from collective.cart.shopping.browser.viewlet import CartArticlesViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class CartArticlesViewletTestCase(IntegrationTestCase):
    """TestCase for CartArticlesViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCartArticlesViewlet
        self.assertTrue(issubclass(CartArticlesViewlet, BaseCartArticlesViewlet))

    @mock.patch('collective.cart.shopping.browser.viewlet.IStock')
    @mock.patch('collective.cart.shopping.browser.viewlet.getMultiAdapter')
    def test_update(self, getMultiAdapter, IStock):
        view = mock.Mock()
        carticle = {'quantity': 1}
        view.shopping_site.get_cart_article.return_value = carticle
        instance = self.create_viewlet(CartArticlesViewlet, view=view)
        self.assertIsNone(instance.update())

        instance.request.form = {'form.update.article': 'uuid', 'quantity': '2'}
        IStock().stock = 4
        IStock().reducible_quantity = 3
        getMultiAdapter().current_base_url.return_value = 'current_base_url'

        from zExceptions import Forbidden
        with self.assertRaises(Forbidden):
            instance.update()

        instance.context.restrictedTraverse = mock.Mock()
        self.assertEqual(instance.update(), 'current_base_url')
        self.assertEqual(carticle['quantity'], 2)
