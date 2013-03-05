from collective.cart.shopping.browser.template import CustomerInfoView

import unittest


class CustomerInfoViewTestCase(unittest.TestCase):
    """TestCase for CustomerInfoView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseView
        self.assertTrue(issubclass(CustomerInfoView, BaseView))

    def test_context(self):
        from collective.cart.shopping.interfaces import ICustomerInfo
        self.assertTrue(getattr(CustomerInfoView, 'grokcore.component.directive.context'), ICustomerInfo)

    def test_name(self):
        self.assertTrue(getattr(CustomerInfoView, 'grokcore.component.directive.name'), 'view')

    def test_template(self):
        self.assertTrue(getattr(CustomerInfoView, 'grokcore.view.directive.template'), 'customer-info')
