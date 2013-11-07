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

        money = self.money('12.40')
        self.create_content('collective.cart.core.Article', context, id='article1', title='Ärticle1', money=money)
        IArticleAdapter().discount_available.return_value = False
        IArticleAdapter().gross.return_value = money
        self.assertEqual(instance.articles(), [{
            'class': 'normal',
            'description': '',
            'discount-available': False,
            'gross': u'12.40 €',
            'money': u'12.40 €',
            'title': 'Ärticle1',
            'url': 'http://nohost/plone/article-container/article1'
        }])

        IArticleAdapter().discount_available.return_value = True
        self.assertEqual(instance.articles(), [{
            'class': 'discount',
            'description': '',
            'discount-available': True,
            'gross': u'12.40 €',
            'money': u'12.40 €',
            'title': 'Ärticle1',
            'url': 'http://nohost/plone/article-container/article1'
        }])
