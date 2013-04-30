# from collective.cart.shopping.browser.viewlet import BillingAndShippingCheckOutViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class BillingAndShippingCheckOutViewletTestCase(IntegrationTestCase):
    """TestCase for BillingAndShippingCheckOutViewlet"""

    def test(self):
        pass

    # def test_subclass(self):
    #     from collective.cart.shopping.browser.viewlet import BaseShoppingSiteRootViewlet
    #     self.assertTrue(issubclass(BillingAndShippingCheckOutViewlet, BaseShoppingSiteRootViewlet))

    # def test_name(self):
    #     self.assertEqual(getattr(BillingAndShippingCheckOutViewlet, 'grokcore.component.directive.name'), 'collective.cart.shopping.billing-and-shipping-check-out')

    # def test_template(self):
    #     self.assertTrue(getattr(BillingAndShippingCheckOutViewlet, 'grokcore.view.directive.template'), 'billing-and-shipping-check-out')

    # def test_viewletmanager(self):
    #     from collective.cart.shopping.browser.viewlet import BillingAndShippingViewletManager
    #     self.assertEqual(getattr(BillingAndShippingCheckOutViewlet, 'grokcore.viewlet.directive.viewletmanager'), BillingAndShippingViewletManager)

    # @mock.patch('plone.protect.authenticator.AuthenticatorView.verify')
    # @mock.patch('collective.cart.shopping.browser.viewlet.IShoppingSite')
    # def test_update(self, IShoppingSite, verify):
    #     instance = self.create_viewlet(BillingAndShippingCheckOutViewlet)
    #     instance.request.form = {'form.buttons.back': True}
    #     verify.return_value = False
    #     from zExceptions import Forbidden
    #     with self.assertRaises(Forbidden):
    #         instance.update()

    #     IShoppingSite().shop.absolute_url.return_value = 'SHOP_URL'
    #     verify.return_value = True
    #     self.assertEqual(instance.update(), 'SHOP_URL/@@cart')

    #     instance.request.form = {'form.to.confirmation': True}
    #     verify.return_value = False
    #     with self.assertRaises(Forbidden):
    #         instance.update()

    #     verify.return_value = True
    #     self.assertEqual(instance.update(), 'SHOP_URL/@@order-confirmation')
