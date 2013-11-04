# -*- coding: utf-8 -*-
from collective.cart.shopping.browser.interfaces import IArticleImagesViewlet
from collective.cart.shopping.browser.viewlet import ArticleImagesViewlet
from collective.cart.shopping.tests.base import IntegrationTestCase


class ArticleImagesViewletTestCase(IntegrationTestCase):
    """TestCase for ArticleImagesViewlet"""

    def test_subclass(self):
        from collective.cart.shopping.browser.viewlet import BaseArticleViewlet
        self.assertTrue(ArticleImagesViewlet, BaseArticleViewlet)
        from collective.cart.shopping.browser.interfaces import IBaseArticleViewlet
        self.assertTrue(issubclass(IArticleImagesViewlet, IBaseArticleViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.shopping.ArticleContainer')
        instance = self.create_viewlet(ArticleImagesViewlet, context)
        self.assertTrue(verifyObject(IArticleImagesViewlet, instance))

    def test_images(self):
        from collective.cart.shopping.browser.view import ArticleView
        article = self.create_content('collective.cart.core.Article')
        self.create_atcontent('Image', article, id='image1', title='Image1', description="Description of Image1")
        self.create_atcontent('Image', article, id='image3', title='Image3', description="Description of Image3")
        self.create_atcontent('Image', article, id='image2', title='Image2', description="Description of Image2")
        view = self.create_view(ArticleView, article)
        instance = self.create_viewlet(ArticleImagesViewlet, article, view=view)
        self.assertEqual(instance.images(), [{
            'description': 'Description of Image1',
            'title': 'Image1',
            'url': 'http://nohost/plone/collective-cart-core-article/image1'
        }, {
            'description': 'Description of Image3',
            'title': 'Image3',
            'url': 'http://nohost/plone/collective-cart-core-article/image3'
        }, {
            'description': 'Description of Image2',
            'title': 'Image2',
            'url': 'http://nohost/plone/collective-cart-core-article/image2'
        }])
