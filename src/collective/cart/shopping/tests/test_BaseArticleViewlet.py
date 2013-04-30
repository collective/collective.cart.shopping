# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IBaseArticleViewlet
from collective.cart.shopping.browser.viewlet import BaseArticleViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class BaseArticleViewletTestCase(IntegrationTestCase):
    """TestCase for BaseArticleViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(BaseArticleViewlet, ViewletBase))
        from collective.base.interfaces import IViewlet
        self.assertTrue(issubclass(IBaseArticleViewlet, IViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(BaseArticleViewlet, context)
        self.assertTrue(verifyObject(IBaseArticleViewlet, instance))
