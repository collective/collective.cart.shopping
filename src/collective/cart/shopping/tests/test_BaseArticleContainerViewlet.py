from collective.cart.shopping.browser.viewlet import BaseArticleContainerViewlet

import unittest


class BaseArticleContainerViewletTestCase(unittest.TestCase):
    """TestCase for BaseArticleContainerViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewlet
        self.assertTrue(issubclass(BaseArticleContainerViewlet, BaseViewlet))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseArticleContainerViewlet, 'martian.martiandirective.baseclass'))

    def test_context(self):
        from collective.cart.shopping.interfaces import IArticleContainer
        self.assertEqual(getattr(BaseArticleContainerViewlet, 'grokcore.component.directive.context'), IArticleContainer)
