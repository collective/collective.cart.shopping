# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IArticleContainerView
from collective.cart.shopping.browser.view import ArticleContainerView
from collective.cart.shopping.tests.base import IntegrationTestCase


class ArticleContainerViewTestCase(IntegrationTestCase):
    """TestCase for ArticleContainerView"""

    def test_subclass(self):
        from Products.Five.browser import BrowserView
        self.assertTrue(issubclass(ArticleContainerView, BrowserView))
        from plone.app.layout.globals.interfaces import IViewView
        self.assertTrue(issubclass(IArticleContainerView, IViewView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.shopping.ArticleContainer')
        instance = self.create_view(ArticleContainerView, context)
        self.assertTrue(verifyObject(IArticleContainerView, instance))

    def test___call__(self):
        context = self.create_content('collective.cart.shopping.ArticleContainer')
        instance = self.create_view(ArticleContainerView, context)
        self.assertEqual(instance.__call__.filename.split('/')[-1], 'article-container.pt')
