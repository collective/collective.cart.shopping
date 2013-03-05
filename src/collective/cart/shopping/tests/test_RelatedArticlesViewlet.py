from collective.cart.shopping.browser.viewlet import RelatedArticlesViewlet

import unittest


class RelatedArticlesViewletTestCase(unittest.TestCase):
    """TestCase for RelatedArticlesViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseArticleViewlet
        self.assertTrue(issubclass(RelatedArticlesViewlet, BaseArticleViewlet))

    def test_name(self):
        self.assertEqual(getattr(RelatedArticlesViewlet, 'grokcore.component.directive.name'), 'collective.cart.shopping.related.articles')

    def test_template(self):
        self.assertEqual(getattr(RelatedArticlesViewlet, 'grokcore.view.directive.template'), 'related-articles')

    def test_view(self):
        from plone.app.layout.globals.interfaces import IViewView
        self.assertEqual(getattr(RelatedArticlesViewlet, 'grokcore.viewlet.directive.view'), IViewView)

    def test_viewletmanager(self):
        from plone.app.layout.viewlets.interfaces import IBelowContent
        self.assertEqual(getattr(RelatedArticlesViewlet, 'grokcore.viewlet.directive.viewletmanager'), IBelowContent)
