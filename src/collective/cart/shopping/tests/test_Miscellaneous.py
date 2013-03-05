# -*- coding: utf-8 -*-
from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.dexterity.utils import createContentInContainer
from zope.lifecycleevent import modified
from zope.publisher.browser import TestRequest
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import directlyProvides


class MiscellaneousTestCase(IntegrationTestCase):
    """TestCase for Miscellaneous"""

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from Products.Five.browser import BrowserView
        from collective.cart.shopping.browser.miscellaneous import Miscellaneous
        self.assertTrue(issubclass(Miscellaneous, BrowserView))

    def create_view(self, context):
        from collective.cart.shopping.browser.miscellaneous import Miscellaneous
        request = TestRequest()
        directlyProvides(request, IAttributeAnnotatable)
        return Miscellaneous(context, request)

    def create_article(self):
        article = createContentInContainer(self.portal, 'collective.cart.core.Article',
            checkConstraints=False, money=Money(Decimal('12.40'), currency='EUR'), vat=Decimal('24.00'))
        modified(article)
        return article

    def test_is_article(self):
        instance = self.create_view(self.portal)
        self.assertFalse(instance.is_article())

        article = self.create_article()
        instance = self.create_view(article)
        self.assertTrue(instance.is_article())
