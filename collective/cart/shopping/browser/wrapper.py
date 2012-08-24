from collective.cart.shipping.browser import wrapper
from collective.cart.shopping.browser.form import ShippingMethodForm


class ShippingMethodFormWrapper(wrapper.ShippingMethodFormWrapper):
    form = ShippingMethodForm
