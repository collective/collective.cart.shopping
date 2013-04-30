from collective.cart.shopping.tests.base import IntegrationTestCase


class TestCase(IntegrationTestCase):
    """TestCase for Shop creation."""

    def test_cart_container_created(self):
        """Test that Cart Container is created within Shop when the Shop is created."""
        from collective.cart.core.interfaces import IShoppingSite
        shop = self.create_content('collective.cart.shopping.Shop')
        self.assertIsNotNone(IShoppingSite(shop).order_container())

    def test_shipping_methods_created(self):
        """Test that Shipping Methods is created within Shop when the Shop is created."""
        shop = self.create_content('collective.cart.shopping.Shop')
        self.assertIsNotNone(shop['shipping-method-container'])
