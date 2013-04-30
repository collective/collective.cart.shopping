# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IBaseArticleView
from collective.cart.shopping.browser.template import BaseArticleView
from collective.cart.shopping.tests.base import IntegrationTestCase


class BaseArticleViewTestCase(IntegrationTestCase):
    """TestCase for BaseArticleView"""

    def test_subclass(self):
        from collective.cart.core.browser.template import BaseFormView
        self.assertTrue(issubclass(BaseArticleView, BaseFormView))
        from collective.cart.core.browser.interfaces import IBaseFormView
        self.assertTrue(issubclass(IBaseArticleView, IBaseFormView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article', title="Ärticle")
        instance = self.create_view(BaseArticleView, context)
        self.assertTrue(verifyObject(IBaseArticleView, instance))

    def test_title(self):
        context = self.create_content('collective.cart.core.Article', title="Ärticle")
        instance = self.create_view(BaseArticleView, context)
        self.assertEqual(instance.title(), 'Ärticle')
