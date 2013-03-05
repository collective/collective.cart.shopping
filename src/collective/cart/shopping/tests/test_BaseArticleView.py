from collective.cart.shopping.browser.template import BaseArticleView
from collective.cart.shopping.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import directlyProvides

import mock


class BaseArticleViewTestCase(IntegrationTestCase):
    """TestCase for BaseArticleView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseView
        self.assertTrue(issubclass(BaseArticleView, BaseView))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseArticleView, 'martian.martiandirective.baseclass'))

    def test_context(self):
        from collective.cart.shopping.interfaces import IArticle
        self.assertTrue(getattr(BaseArticleView, 'grokcore.component.directive.context'), IArticle)

    def create_view(self, context):
        request = TestRequest()
        directlyProvides(request, IAttributeAnnotatable)
        return BaseArticleView(context, request)

    @mock.patch('collective.cart.shopping.browser.template.IArticleAdapter')
    def test_title(self, IArticleAdapter):
        context = mock.Mock()
        instance = self.create_view(context)
        IArticleAdapter().title = 'TITLE'
        self.assertEqual(instance.title, 'TITLE')
