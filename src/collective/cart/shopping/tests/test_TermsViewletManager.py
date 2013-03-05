from collective.cart.shopping.browser.viewlet import TermsViewletManager

import unittest


class TermsViewletManagerTestCase(unittest.TestCase):
    """TestCase for TermsViewletManager"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseViewletManager
        self.assertTrue(issubclass(TermsViewletManager, BaseViewletManager))

    def test_name(self):
        self.assertTrue(getattr(TermsViewletManager, 'grokcore.component.directive.name'),
            'collective.cart.shopping.terms.manager')
