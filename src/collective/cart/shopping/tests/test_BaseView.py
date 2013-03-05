from collective.cart.shopping.browser.template import BaseView

import unittest


class BaseViewTestCase(unittest.TestCase):
    """TestCase for BaseView"""

    def test_templatedir(self):
        from collective.cart.shopping.browser import template
        self.assertEqual(getattr(template, 'grokcore.view.directive.templatedir'), 'templates')

    def test_subclass(self):
        from five.grok import View
        self.assertTrue(issubclass(BaseView, View))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseView, 'martian.martiandirective.baseclass'))

    def test_layer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        self.assertEqual(getattr(BaseView, 'grokcore.view.directive.layer'), ICollectiveCartShoppingLayer)

    def test_require(self):
        self.assertEqual(getattr(BaseView, 'grokcore.security.directive.require'), ['zope2.View'])
