# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.template import ArticleView
from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import directlyProvides
from zope.lifecycleevent import modified
from zope.publisher.browser import TestRequest

import mock


class ArticleViewTestCase(IntegrationTestCase):
    """TestCase for ArticleView"""

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseArticleView
        self.assertTrue(issubclass(ArticleView, BaseArticleView))

    def test_name(self):
        self.assertEqual(getattr(ArticleView, 'grokcore.component.directive.name'), 'view')

    def test_template(self):
        self.assertEqual(getattr(ArticleView, 'grokcore.view.directive.template'), 'article')

    def create_article(self):
        article = createContentInContainer(self.portal, 'collective.cart.core.Article', id='article',
            checkConstraints=False, money=Money(Decimal('12.40'), currency='EUR'), vat=Decimal('24.00'))
        modified(article)
        return article

    def create_image(self, parent, **kwargs):
        image = parent[parent.invokeFactory('Image', **kwargs)]
        image.reindexObject()
        return image

    def create_view(self, context):
        request = TestRequest()
        directlyProvides(request, IAttributeAnnotatable)
        return ArticleView(context, request)

    def test_images(self):
        article = self.create_article()
        instance = self.create_view(article)
        self.assertEqual(len(instance.images), 0)

        self.create_image(article, id='image1', title='Imäge1', description='Description of Imäge1')
        self.assertEqual(instance.images, [{
            'description': 'Description of Imäge1',
            'title': 'Imäge1',
            'url': 'http://nohost/plone/article/image1',
        }])

        self.create_image(article, id='image3', title='Imäge3', description='Description of Imäge3')
        self.create_image(article, id='image2', title='Imäge2', description='Description of Imäge2')
        self.create_image(self.portal, id='image4', title='Imäge4', description='Description of Imäge4')

        self.assertEqual([image['title'] for image in instance.images], ['Imäge1', 'Imäge3', 'Imäge2'])

    @mock.patch('collective.cart.shopping.browser.template.IArticleAdapter')
    def test_gross(self, IArticleAdapter):
        IArticleAdapter().gross = 'GROSS'
        context = mock.Mock()
        instance = self.create_view(context)
        self.assertEqual(instance.gross, 'GROSS')

    @mock.patch('collective.cart.shopping.browser.template.IArticleAdapter')
    def test_discount_end(self, IArticleAdapter):
        IArticleAdapter().discount_end = 'DISCOUNT_END'
        context = mock.Mock()
        instance = self.create_view(context)
        self.assertEqual(instance.discount_end, 'DISCOUNT_END')

    @mock.patch('collective.cart.shopping.browser.template.IArticleAdapter')
    def test_image_url(self, IArticleAdapter):
        IArticleAdapter().image_url = 'IMAGE_URL'
        context = mock.Mock()
        instance = self.create_view(context)
        self.assertEqual(instance.image_url, 'IMAGE_URL')
