# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IRelatedArticlesViewlet
from collective.cart.shopping.browser.viewlet import RelatedArticlesViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class RelatedArticlesViewletTestCase(IntegrationTestCase):
    """TestCase for RelatedArticlesViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase as Base
        self.assertTrue(issubclass(RelatedArticlesViewlet, Base))
        from collective.base.interfaces import IViewlet as Base
        self.assertTrue(issubclass(IRelatedArticlesViewlet, Base))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(RelatedArticlesViewlet, context)
        self.assertTrue(verifyObject(IRelatedArticlesViewlet, instance))

    def test_index(self):
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(RelatedArticlesViewlet, context)
        self.assertEqual(instance.index.filename.split('/')[-1], 'related-articles.pt')

    def test_articles(self):
        from Products.CMFCore.utils import getToolByName
        from collective.cart.core.interfaces import IShoppingSiteRoot
        from plone.uuid.interfaces import IUUID
        from zope.interface import alsoProvides
        from zope.lifecycleevent import modified
        alsoProvides(self.portal, IShoppingSiteRoot)
        workflow = getToolByName(self.portal, 'portal_workflow')
        context = self.create_content('collective.cart.core.Article')
        article1 = self.create_content('collective.cart.core.Article', money=self.money('10.00'), title='Ärticle1')
        workflow.doActionFor(article1, 'publish')
        uuid1 = IUUID(article1)
        modified(article1)
        article2 = self.create_content('collective.cart.core.Article', money=self.money('20.00'), title='Ärticle2')
        workflow.doActionFor(article2, 'publish')
        uuid2 = IUUID(article2)
        modified(article2)
        context.related_articles = [uuid1, uuid2]
        instance = self.create_viewlet(RelatedArticlesViewlet, context)
        self.assertEqual(instance.articles(), [{
            'gross': self.money('10.00'),
            'image_url': 'http://nohost/plone/fallback.png',
            'title': 'Ärticle1',
            'url': 'http://nohost/plone/article1'
        }, {
            'gross': self.money('20.00'),
            'image_url': 'http://nohost/plone/fallback.png',
            'title': 'Ärticle2',
            'url': 'http://nohost/plone/article2'
        }])
