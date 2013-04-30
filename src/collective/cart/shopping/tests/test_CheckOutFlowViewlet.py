# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import ICheckOutFlowViewlet
from collective.cart.shopping.browser.viewlet import CheckOutFlowViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class CheckOutFlowViewletTestCase(IntegrationTestCase):
    """TestCase for CheckOutFlowViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(CheckOutFlowViewlet, ViewletBase))
        from collective.base.interfaces import IViewlet
        self.assertTrue(issubclass(ICheckOutFlowViewlet, IViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(CheckOutFlowViewlet, context)
        self.assertTrue(verifyObject(ICheckOutFlowViewlet, instance))

    def test__get_title(self):
        instance = self.create_viewlet(CheckOutFlowViewlet)
        instance.view = mock.Mock()
        brain = mock.Mock()
        brain.Title = 'TITLE'
        instance.view.shopping_site().get_brain_for_text.return_value = brain
        self.assertEqual(instance._get_title('view'), 'TITLE')
