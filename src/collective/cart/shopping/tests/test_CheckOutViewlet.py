from collective.cart.shopping.browser.viewlet import CheckOutViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class CheckOutViewletTestCase(IntegrationTestCase):
    """TestCase for CheckOutViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseCartViewlet
        self.assertTrue(issubclass(CheckOutViewlet, BaseCartViewlet))

    def test_name(self):
        self.assertEqual(getattr(CheckOutViewlet, 'grokcore.component.directive.name'), 'collective.cart.shopping.checkout')

    def test_template(self):
        self.assertEqual(getattr(CheckOutViewlet, 'grokcore.view.directive.template'), 'cart-checkout')

    @mock.patch('plone.protect.authenticator.AuthenticatorView.verify')
    @mock.patch('collective.cart.shopping.browser.viewlet.IShoppingSite')
    def test_update(self, IShoppingSite, verify):
        instance = self.create_viewlet(CheckOutViewlet)
        self.assertIsNone(instance.update())

        instance.request.form = {'form.checkout': True}
        self.portal.absolute_url = mock.Mock(return_value='portal_url')

        verify.return_value = False
        from zExceptions import Forbidden
        with self.assertRaises(Forbidden):
            instance.update()

        verify.return_value = True
        self.assertEqual(instance.update(), 'portal_url/@@billing-and-shipping')

        instance.request.form = {'form.clear.cart': True}
        verify.return_value = False
        with self.assertRaises(Forbidden):
            instance.update()

        self.portal.restrictedTraverse = mock.Mock()
        self.portal.restrictedTraverse().current_base_url = mock.Mock(return_value='current_base_url')
        self.assertEqual(instance.update(), 'current_base_url')
        self.assertTrue(IShoppingSite().remove_cart_articles.called)
