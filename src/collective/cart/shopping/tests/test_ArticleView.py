# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IArticleView
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

    def test_subclass(self):
        from collective.cart.shopping.browser.template import BaseArticleView
        self.assertTrue(issubclass(ArticleView, BaseArticleView))
        from collective.cart.shopping.browser.interfaces import IBaseArticleView
        self.assertTrue(issubclass(IArticleView, IBaseArticleView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.Article', title="Ärticle")
        instance = self.create_view(ArticleView, context)
        self.assertTrue(verifyObject(IArticleView, instance))

    # def test___call__(self):
    #     context = mock.Mock()
    #     instance = self.create_view(ArticleView, context)
    #     self.assertEqual(instance.__call__.filename.split('/')[-1], 'article.pt')

    # def test_images(self):
    #     context = self.create_content('collective.cart.core.Article', id='article')
    #     instance = self.create_view(ArticleView, context)
    #     self.assertEqual(len(instance.images()), 0)

    #     self.create_atcontent('Image', context, id='image1', title='Imäge1', description='Description of Imäge1')
    #     self.assertEqual(instance.images(), [{
    #         'description': 'Description of Imäge1',
    #         'title': 'Imäge1',
    #         'url': 'http://nohost/plone/article/image1',
    #     }])

    #     self.create_atcontent('Image', context, id='image3', title='Imäge3', description='Description of Imäge3')
    #     self.create_atcontent('Image', context, id='image2', title='Imäge2', description='Description of Imäge2')
    #     self.create_atcontent('Image', id='image4', title='Imäge4', description='Description of Imäge4')

    #     self.assertEqual([image['title'] for image in instance.images()], ['Imäge1', 'Imäge3', 'Imäge2'])

    # @mock.patch('collective.cart.shopping.browser.template.IArticleAdapter')
    # def test_gross(self, IArticleAdapter):
    #     IArticleAdapter().gross.return_value = 'GROSS'
    #     context = mock.Mock()
    #     instance = self.create_view(ArticleView, context)
    #     self.assertEqual(instance.gross(), 'GROSS')

    # @mock.patch('collective.cart.shopping.browser.template.IArticleAdapter')
    # def test_discount_end(self, IArticleAdapter):
    #     IArticleAdapter().discount_end.return_value = 'DISCOUNT_END'
    #     context = mock.Mock()
    #     instance = self.create_view(ArticleView, context)
    #     self.assertEqual(instance.discount_end(), 'DISCOUNT_END')

    # @mock.patch('collective.cart.shopping.browser.template.IArticleAdapter')
    # def test_image_url(self, IArticleAdapter):
    #     IArticleAdapter().image_url.return_value = 'IMAGE_URL'
    #     context = mock.Mock()
    #     instance = self.create_view(ArticleView, context)
    #     self.assertEqual(instance.image_url(), 'IMAGE_URL')
