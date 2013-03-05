from collective.cart.shopping.browser.viewlet import BaseViewletManager

import unittest


class BaseViewletManagerTestCase(unittest.TestCase):
    """TestCase for BaseViewletManager"""

    def test_templatedir(self):
        from collective.cart.shopping.browser import viewlet
        self.assertEqual(getattr(viewlet, 'grokcore.view.directive.templatedir'), 'viewlets')

    def test_subclass(self):
        from plone.app.viewletmanager.manager import OrderedViewletManager
        from five.grok import ViewletManager
        self.assertTrue(issubclass(BaseViewletManager, (OrderedViewletManager, ViewletManager)))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseViewletManager, 'martian.martiandirective.baseclass'))

    def test_context(self):
        from collective.cart.core.interfaces import IShoppingSiteRoot
        self.assertTrue(getattr(BaseViewletManager, 'grokcore.component.directive.context'), IShoppingSiteRoot)

    def test_layer(self):
        from collective.cart.shopping.browser.interfaces import ICollectiveCartShoppingLayer
        self.assertEqual(getattr(BaseViewletManager, 'grokcore.view.directive.layer'), ICollectiveCartShoppingLayer)
