# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import getToolByName
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.adapter.article import ArticleAdapter
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.interface import alsoProvides
from zope.lifecycleevent import modified

import mock


class ArticleAdapterTestCase(IntegrationTestCase):
    """TestCase for ArticleAdapter"""

    def test_subclass(self):
        from collective.cart.core.adapter.article import ArticleAdapter as BaseArticleAdapter
        self.assertTrue(issubclass(ArticleAdapter, BaseArticleAdapter))
        from collective.cart.core.interfaces import IArticleAdapter as IBaseArticleAdapter
        self.assertTrue(issubclass(IArticleAdapter, IBaseArticleAdapter))

    def test_instance(self):
        article = self.create_content('collective.cart.core.Article')
        self.assertIsInstance(IArticleAdapter(article), ArticleAdapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        article = self.create_content('collective.cart.core.Article')
        self.assertTrue(verifyObject(IArticleAdapter, IArticleAdapter(article)))

    def test_discount_available(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=24.0)
        adapter = IArticleAdapter(article1)
        self.assertFalse(adapter.discount_available())

        from collective.behavior.discount.interfaces import IDiscount
        discount = IDiscount(article1)
        discount.discount_enabled = True
        self.assertFalse(adapter.discount_available())

        from datetime import date
        today = date.today()
        from datetime import timedelta
        discount.discount_end = today - timedelta(1)
        self.assertFalse(adapter.discount_available())

        discount.discount_end = today + timedelta(1)
        self.assertTrue(adapter.discount_available())

        article1.discount_end = None
        discount.discount_start = today + timedelta(1)
        self.assertFalse(adapter.discount_available())

        discount.discount_start = today - timedelta(1)
        self.assertTrue(adapter.discount_available())

        discount.discount_end = today - timedelta(1)
        self.assertFalse(adapter.discount_available())

        discount.discount_end = today + timedelta(1)
        self.assertTrue(adapter.discount_available())

        discount.discount_start = today + timedelta(1)
        self.assertFalse(adapter.discount_available())

    def test_image_url(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=24.0)
        adapter = IArticleAdapter(article1)
        self.assertEqual(adapter.image_url(), 'http://nohost/plone/fallback.png')

        article2 = self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ1', money=self.money('12.40'), vat_rate=24.0)
        adapter = IArticleAdapter(article2)
        self.assertEqual(adapter.image_url(), 'http://nohost/plone/fallback.png')

        article1.image = mock.Mock()
        self.assertEqual(adapter.image_url(), 'http://nohost/plone/article1/@@images/image')

        adapter.context.image = mock.Mock()
        self.assertEqual(adapter.image_url(), 'http://nohost/plone/article1/article2/@@images/image')

