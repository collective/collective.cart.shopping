# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from collective.cart.shopping.tests.base import IntegrationTestCase


class TestCase(IntegrationTestCase):
    """TestCase subscriber"""

    def test_make_subarticles_private(self):
        wftool = getToolByName(self.portal, "portal_workflow")
        article1 = self.create_content('collective.cart.core.Article', title='Ärticle1', sku='SKÖ1', money=self.money('12.40'), vat_rate=24.0)
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'private')

        # make public
        wftool.doActionFor(article1, 'publish')
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'published')

        # make article1 use_subarticle
        article1.use_subarticle = True
        article11 = self.create_content('collective.cart.core.Article', parent=article1, title='Ärticle11', sku='SKÖ11', money=self.money('12.40'), vat_rate=24.0)
        article12 = self.create_content('collective.cart.core.Article', parent=article1, title='Ärticle12', sku='SKÖ12', money=self.money('12.40'), vat_rate=24.0)

        # make private
        wftool.doActionFor(article1, 'retract')
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'private')

        # make public
        wftool.doActionFor(article1, 'publish')
        wftool.doActionFor(article11, 'publish')
        status = wftool.getStatusOf("simple_publication_workflow", article11)
        self.assertEqual(status['review_state'], 'published')
        wftool.doActionFor(article12, 'publish')
        status = wftool.getStatusOf("simple_publication_workflow", article12)
        self.assertEqual(status['review_state'], 'published')

        # make private
        wftool.doActionFor(article1, 'retract')
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article11)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article12)
        self.assertEqual(status['review_state'], 'private')

        # make public
        wftool.doActionFor(article1, 'publish')
        wftool.doActionFor(article11, 'publish')
        wftool.doActionFor(article12, 'publish')

        article111 = self.create_content('collective.cart.core.Article', parent=article11, title='Ärticle111', sku='SKÖ111', money=self.money('12.40'), vat_rate=24.0)
        article112 = self.create_content('collective.cart.core.Article', parent=article11, title='Ärticle112', sku='SKÖ112', money=self.money('12.40'), vat_rate=24.0)
        article113 = self.create_content('collective.cart.core.Article', parent=article11, title='Ärticle113', sku='SKÖ113', money=self.money('12.40'), vat_rate=24.0)
        wftool.doActionFor(article111, 'publish')
        wftool.doActionFor(article112, 'publish')

        # make private
        wftool.doActionFor(article1, 'retract')
        status = wftool.getStatusOf("simple_publication_workflow", article1)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article11)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article12)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article111)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article112)
        self.assertEqual(status['review_state'], 'private')
        status = wftool.getStatusOf("simple_publication_workflow", article113)
        self.assertEqual(status['review_state'], 'private')
