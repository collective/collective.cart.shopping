from collective.cart.shopping.browser.viewlet import BillingAndShippingShippingMethodsViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class BillingAndShippingShippingMethodsViewletTestCase(IntegrationTestCase):
    """TestCase for BillingAndShippingShippingMethodsViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(BillingAndShippingShippingMethodsViewlet, ViewletBase))
