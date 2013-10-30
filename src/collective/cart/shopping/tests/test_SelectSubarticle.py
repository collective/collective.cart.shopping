# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.ajax import SelectSubarticle
from collective.cart.shopping.tests.base import IntegrationTestCase

import mock


class SelectSubarticleTestCase(IntegrationTestCase):
    """TestCase for SelectSubarticle"""

    def test_subclass(self):
        from Products.Five.browser import BrowserView as Base
        self.assertTrue(issubclass(SelectSubarticle, Base))

    def test___call___Forbidden(self):
        instance = self.create_view(SelectSubarticle)
        from zExceptions import Forbidden
        with self.assertRaises(Forbidden):
            instance()

    @mock.patch('plone.protect.authenticator.AuthenticatorView.verify')
    def test___call__(self, verify):
        context = self.create_content('collective.cart.core.Article')
        instance = self.create_view(SelectSubarticle, context)
        self.assertIsNone(instance())

        instance.request.form = {'uuid': 'UUID'}
        self.assertIsNone(instance())

        article1 = self.create_content('collective.cart.core.Article', context)
        from plone.uuid.interfaces import IUUID
        uuid1 = IUUID(article1)

        instance.request.form = {'uuid': uuid1}
        self.assertIsNotNone(instance())
