from collective.cart.shopping.adapter.content_listing_object import ArticleContentListingObject
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.app.contentlisting.interfaces import IContentListingObject

import mock


class ArticleContentListingObjectTestCase(IntegrationTestCase):
    """TestCase for ArticleContentListingObject"""

    def test_subclass(self):
        from plone.app.contentlisting.realobject import RealContentListingObject as Base
        self.assertTrue(issubclass(ArticleContentListingObject, Base))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        article = self.create_content('collective.cart.core.Article')
        instance = IContentListingObject(article)
        self.assertTrue(verifyObject(IContentListingObject, instance))

    def test__repr_(self):
        article = self.create_content('collective.cart.core.Article')
        instance = IContentListingObject(article)
        self.assertEqual(instance.__repr__(), '<collective.cart.shopping.adapter.content_listing_object.ArticleContentListingObject instance at /plone/collective-cart-core-article>')

    def test_discount_available(self):
        article = self.create_content('collective.cart.core.Article')
        instance = IContentListingObject(article)
        self.assertFalse(instance.discount_available())

        instance.adapter = mock.Mock()
        instance.adapter.discount_available.ruturn_value = True
        self.assertTrue(instance.discount_available())

    def test_klass(self):
        article = self.create_content('collective.cart.core.Article')
        instance = IContentListingObject(article)
        self.assertEqual(instance.klass(), 'normal')

        instance.discount_available = mock.Mock()
        self.assertEqual(instance.klass(), 'discount')

    def test_gross(self):
        article = self.create_content('collective.cart.core.Article')
        instance = IContentListingObject(article)
        instance.shopping_site = mock.Mock()
        instance.adapter = mock.Mock()
        self.assertEqual(instance.gross(), instance.shopping_site.format_money())

    def test_money(self):
        article = self.create_content('collective.cart.core.Article')
        instance = IContentListingObject(article)
        instance.shopping_site = mock.Mock()
        instance._realobject.money = self.money('12.40')
        self.assertEqual(instance.money(), instance.shopping_site.format_money())

    def test_CroppedDescription(self):
        article = self.create_content('collective.cart.core.Article')
        instance = IContentListingObject(article)
        with self.assertRaises(NotImplementedError):
            instance.CroppedDescription()

    def test_getSize(self):
        article = self.create_content('collective.cart.core.Article')
        instance = IContentListingObject(article)
        with self.assertRaises(NotImplementedError):
            instance.getSize()
