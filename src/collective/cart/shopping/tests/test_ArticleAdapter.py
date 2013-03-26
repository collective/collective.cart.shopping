# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import getToolByName
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.interface import alsoProvides
from zope.lifecycleevent import modified

import mock


class ArticleAdapterTestCase(IntegrationTestCase):
    """TestCase for ArticleAdapter"""

    def test_subclass(self):
        from collective.cart.core.adapter.article import ArticleAdapter as BaseArticleAdapter
        from collective.cart.shopping.adapter.article import ArticleAdapter
        self.assertTrue(issubclass(ArticleAdapter, BaseArticleAdapter))
        from collective.cart.core.interfaces import IArticleAdapter as IBaseArticleAdapter
        self.assertTrue(issubclass(IArticleAdapter, IBaseArticleAdapter))

    def test_context(self):
        from collective.cart.shopping.adapter.article import ArticleAdapter
        from collective.cart.shopping.interfaces import IArticle
        self.assertEqual(getattr(ArticleAdapter, 'grokcore.component.directive.context'), IArticle)

    def test_provides(self):
        from collective.cart.shopping.adapter.article import ArticleAdapter
        self.assertEqual(getattr(ArticleAdapter, 'grokcore.component.directive.provides'), IArticleAdapter)

    def test_instance(self):
        from collective.cart.shopping.adapter.article import ArticleAdapter
        article = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        self.assertIsInstance(IArticleAdapter(article), ArticleAdapter)

    def test_instance__provides(self):
        article = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        self.assertEqual(getattr(IArticleAdapter(article), 'grokcore.component.directive.provides'), IArticleAdapter)

    def test_addable_to_cart(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertFalse(adapter.addable_to_cart)

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertTrue(adapter.addable_to_cart)

        adapter.context.use_subarticle = True
        self.assertFalse(adapter.addable_to_cart)

        adapter.context.use_subarticle = False
        self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        self.assertFalse(adapter.addable_to_cart)

    def test_articles_in_article(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertEqual(len(adapter.articles_in_article), 0)

        self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ2',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'), salable=True)
        self.assertEqual(len(adapter.articles_in_article), 1)

        adapter.context.use_subarticle = True
        self.assertEqual(len(adapter.articles_in_article), 0)

    def test_subarticles__zero(self):
        article = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        self.assertEqual(len(IArticleAdapter(article).subarticles), 0)

    def test_subarticles__one(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'), salable=True)
        article2 = self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ2',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'), salable=True)
        self.assertEqual(len(IArticleAdapter(article1).subarticles), 1)

        article2.salable = False
        modified(article2)
        self.assertEqual(len(IArticleAdapter(article1).subarticles), 0)

    @mock.patch('collective.cart.shopping.adapter.article.IStock')
    def test_subarticles_option(self, IStock):
        from collective.cart.core.interfaces import IShoppingSiteRoot
        from plone.uuid.interfaces import IUUID
        from zope.interface import alsoProvides
        alsoProvides(self.portal, IShoppingSiteRoot)
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertEqual(len(adapter.subarticles_option), 0)

        article2 = self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'), salable=True)
        IStock().stock = 0
        self.assertEqual(len(adapter.subarticles_option), 0)

        IStock().stock = 10
        self.assertEqual(adapter.subarticles_option, [{
            'locale_gross': u'12.40 €',
            'title': u'Ärticle2',
            'uuid': IUUID(article2)
        }])

    def test_subarticle_addable_to_cart(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertFalse(adapter.subarticle_addable_to_cart)

        from collective.cart.core.interfaces import IShoppingSiteRoot
        from zope.interface import alsoProvides
        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertFalse(adapter.subarticle_addable_to_cart)

        adapter.context.use_subarticle = True
        self.assertTrue(adapter.subarticle_addable_to_cart)

        from zope.interface import noLongerProvides
        noLongerProvides(self.portal, IShoppingSiteRoot)
        self.assertFalse(adapter.subarticle_addable_to_cart)

    @mock.patch('collective.cart.shopping.adapter.article.IStock')
    def test_subarticle_soldout(self, IStock):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertTrue(adapter.subarticle_soldout)

        IStock().stock = 10
        self.assertTrue(adapter.subarticle_soldout)

        self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'), salable=True)
        self.assertFalse(adapter.subarticle_soldout)

        IStock().stock = 0
        self.assertTrue(adapter.subarticle_soldout)

    @mock.patch('collective.cart.shopping.adapter.article.IStock')
    def test_subarticle_quantity_max(self, IStock):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertEqual(adapter.subarticle_quantity_max, 0)

        self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ1',
            money=self.money('12.40'), vat_rate=self.decimal('24.00'), salable=True)
        IStock().stock = 0
        self.assertEqual(adapter.subarticle_quantity_max, 0)

        IStock().stock = 10
        self.assertEqual(adapter.subarticle_quantity_max, 10)

    @mock.patch('collective.cart.shopping.adapter.article.IStock')
    def test_quantity_max(self, IStock):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        IStock().stock = 0
        IStock().reducible_quantity = 0
        self.assertEqual(adapter.quantity_max, 0)

        IStock().stock = 10
        self.assertEqual(adapter.quantity_max, 0)

        IStock().reducible_quantity = 5
        self.assertEqual(adapter.quantity_max, 5)

        IStock().reducible_quantity = 15
        self.assertEqual(adapter.quantity_max, 10)

        from collective.cart.core.interfaces import IShoppingSiteRoot
        from zope.interface import alsoProvides
        alsoProvides(self.portal, IShoppingSiteRoot)
        from plone.uuid.interfaces import IUUID
        uuid = IUUID(article1)
        session = getToolByName(self.portal, 'session_data_manager').getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {uuid: {'quantity': 2}}})
        self.assertEqual(adapter.quantity_max, 8)

    def test__update_existing_cart_article(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        items = {'quantity': 0}
        kwargs = {'quantity': 0}
        adapter._update_existing_cart_article(items, **kwargs)
        self.assertEqual(items['quantity'], 0)

        items = {'quantity': 2}
        kwargs = {'quantity': 1}
        adapter._update_existing_cart_article(items, **kwargs)
        self.assertEqual(items['quantity'], 3)

    def test_discount_available(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertFalse(adapter.discount_available)

        from collective.behavior.discount.interfaces import IDiscount
        discount = IDiscount(article1)
        discount.discount_enabled = True
        self.assertFalse(adapter.discount_available)

        from datetime import date
        today = date.today()
        from datetime import timedelta
        discount.discount_end = today - timedelta(1)
        self.assertFalse(adapter.discount_available)

        discount.discount_end = today + timedelta(1)
        self.assertTrue(adapter.discount_available)

        article1.discount_end = None
        discount.discount_start = today + timedelta(1)
        self.assertFalse(adapter.discount_available)

        discount.discount_start = today - timedelta(1)
        self.assertTrue(adapter.discount_available)

        discount.discount_end = today - timedelta(1)
        self.assertFalse(adapter.discount_available)

        discount.discount_end = today + timedelta(1)
        self.assertTrue(adapter.discount_available)

        discount.discount_start = today + timedelta(1)
        self.assertFalse(adapter.discount_available)

    def test_discount_end(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertIsNone(adapter.discount_end)

        from collective.behavior.discount.interfaces import IDiscount
        discount = IDiscount(article1)
        discount.discount_enabled = True
        from datetime import date
        today = date.today()
        from datetime import timedelta
        end = today + timedelta(1)
        discount.discount_end = end
        from datetime import datetime
        from datetime import time
        dt = datetime.combine(end, time())
        self.assertEqual(adapter.discount_end, getToolByName(self.portal, 'translation_service').ulocalized_time(dt))

    def test_gross(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        from decimal import Decimal
        from moneyed import Money
        self.assertEqual(adapter.gross, Money(Decimal('12.40'), 'EUR'))

        from collective.behavior.discount.interfaces import IDiscount
        discount = IDiscount(article1)
        article1.discount_gross = self.money('10.00')
        self.assertEqual(adapter.gross, self.money('12.40'))

        discount.discount_enabled = True
        from datetime import date
        today = date.today()
        from datetime import timedelta
        discount.discount_end = today + timedelta(1)
        self.assertEqual(adapter.gross, self.money('10.00'))

    def test_vat(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        from decimal import Decimal
        from moneyed import Money
        self.assertEqual(adapter.vat, self.money('2.40'))

        from collective.behavior.discount.interfaces import IDiscount
        discount = IDiscount(article1)
        article1.discount_vat = Money(Decimal('1.20'), 'EUR')
        self.assertEqual(adapter.vat, Money(Decimal('2.40'), 'EUR'))

        discount.discount_enabled = True
        from datetime import date
        today = date.today()
        from datetime import timedelta
        discount.discount_end = today + timedelta(1)
        self.assertEqual(adapter.vat, Money(Decimal('1.20'), 'EUR'))

    def test_net(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        from decimal import Decimal
        from moneyed import Money
        self.assertEqual(adapter.net, Money(Decimal('10.00'), 'EUR'))

        from collective.behavior.discount.interfaces import IDiscount
        discount = IDiscount(article1)
        article1.discount_net = Money(Decimal('5.00'), 'EUR')
        self.assertEqual(adapter.net, Money(Decimal('10.00'), 'EUR'))

        discount.discount_enabled = True
        from datetime import date
        today = date.today()
        from datetime import timedelta
        discount.discount_end = today + timedelta(1)
        self.assertEqual(adapter.net, Money(Decimal('5.00'), 'EUR'))

    @mock.patch('collective.cart.shopping.adapter.article.IStock')
    def test_soldout(self, IStock):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertTrue(adapter.soldout)

        from collective.cart.core.interfaces import IShoppingSiteRoot
        from zope.interface import alsoProvides
        alsoProvides(self.portal, IShoppingSiteRoot)
        IStock().stock = 0
        self.assertTrue(adapter.soldout)

        IStock().stock = 10
        self.assertFalse(adapter.soldout)

    def test_image_url(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertEqual(adapter.image_url, 'http://nohost/plone/fallback.png')

        article2 = self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article2)
        self.assertEqual(adapter.image_url, 'http://nohost/plone/fallback.png')

        article1.image = mock.Mock()
        self.assertEqual(adapter.image_url, 'http://nohost/plone/article1/@@images/image')

        adapter.context.image = mock.Mock()
        self.assertEqual(adapter.image_url, 'http://nohost/plone/article1/article2/@@images/image')

    def test_title(self):
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article1)
        self.assertEqual(adapter.title, 'Ärticle1')

        article2 = self.create_content('collective.cart.core.Article', article1, title='Ärticle2', sku='SKÖ2', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article2)
        self.assertEqual(adapter.title, 'Ärticle1 Ärticle2')

        article3 = self.create_content('collective.cart.core.Article', article2, title='Ärticle3', sku='SKÖ3', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article3)
        self.assertEqual(adapter.title, 'Ärticle1 Ärticle2 Ärticle3')

        article4 = self.create_content('collective.cart.core.Article', article3, title='Ärticle4', sku='SKÖ4', money=self.money('12.40'), vat_rate=self.decimal('24.00'))
        adapter = IArticleAdapter(article4)
        self.assertEqual(adapter.title, 'Ärticle2 Ärticle3 Ärticle4')
