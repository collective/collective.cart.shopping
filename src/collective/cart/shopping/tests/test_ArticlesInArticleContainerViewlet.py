# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.viewlet import ArticlesInArticleContainerViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class ArticlesInArticleContainerViewletTestCase(IntegrationTestCase):
    """TestCase for ArticlesInArticleContainerViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseArticleContainerViewlet
        self.assertTrue(issubclass(ArticlesInArticleContainerViewlet, BaseArticleContainerViewlet))

    def test_name(self):
        self.assertEqual(getattr(ArticlesInArticleContainerViewlet, 'grokcore.component.directive.name'),
            'collective.cart.core.articles-in-articlecontainer')

    def test_template(self):
        self.assertEqual(getattr(ArticlesInArticleContainerViewlet, 'grokcore.view.directive.template'),
            'articles-in-articlecontainer')

    def test_viewletmanager(self):
        from collective.cart.shopping.browser.viewlet import ArticleContainerViewletManager
        self.assertEqual(getattr(ArticlesInArticleContainerViewlet, 'grokcore.viewlet.directive.viewletmanager'),
            ArticleContainerViewletManager)

    @mock.patch('collective.cart.shopping.browser.viewlet.IArticleAdapter')
    def test_articles(self, IArticleAdapter):
        container = self.create_content('collective.cart.shopping.ArticleContainer', id='article-container')
        instance = self.create_viewlet(ArticlesInArticleContainerViewlet, container)
        self.assertEqual(len(instance.articles), 0)

        self.create_content('collective.cart.core.Article', container, id='article1', title='Ärticle1',
            money=self.money('12.40'), vat=self.decimal('24.00'))
        IArticleAdapter().discount_available = False
        IArticleAdapter().locale_gross = 'LOCALE_GROSS'
        IArticleAdapter().locale_money = 'LOCALE_MONEY'
        self.assertEqual(instance.articles, [{
            'class': 'normal',
            'discount-available': False,
            'locale_gross': 'LOCALE_GROSS',
            'locale_money': 'LOCALE_MONEY',
            'title': 'Ärticle1',
            'url': 'http://nohost/plone/article-container/article1'
        }])

        IArticleAdapter().discount_available = True
        self.assertEqual(instance.articles, [{
            'class': 'discount',
            'discount-available': True,
            'locale_gross': 'LOCALE_GROSS',
            'locale_money': 'LOCALE_MONEY',
            'title': 'Ärticle1',
            'url': 'http://nohost/plone/article-container/article1'
        }])
