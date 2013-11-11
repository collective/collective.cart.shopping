# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IArticlesInArticleContainerViewlet
from collective.cart.shopping.browser.viewlet import ArticlesInArticleContainerViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class ArticlesInArticleContainerViewletTestCase(IntegrationTestCase):
    """TestCase for ArticlesInArticleContainerViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(ArticlesInArticleContainerViewlet, ViewletBase))
        from collective.base.interfaces import IViewlet
        self.assertTrue(issubclass(IArticlesInArticleContainerViewlet, IViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.shopping.ArticleContainer')
        instance = self.create_viewlet(ArticlesInArticleContainerViewlet, context)
        self.assertTrue(verifyObject(IArticlesInArticleContainerViewlet, instance))

    def test_index(self):
        context = self.create_content('collective.cart.shopping.ArticleContainer')
        instance = self.create_viewlet(ArticlesInArticleContainerViewlet, context)
        self.assertEqual(instance.index.filename.split('/')[-1], 'articles-in-article-container.pt')

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_articles(self, IArticleAdapter):
        context = self.create_content('collective.cart.shopping.ArticleContainer', id='article-container')
        instance = self.create_viewlet(ArticlesInArticleContainerViewlet, context)
        self.assertEqual(len(instance.articles()), 0)
