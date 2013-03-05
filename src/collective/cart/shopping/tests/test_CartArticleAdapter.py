# -*- coding: utf-8 -*-
from collective.cart.shopping.tests.base import IntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.dexterity.utils import createContentInContainer
from zope.lifecycleevent import modified


class CartArticleAdapterTestCase(IntegrationTestCase):
    """TestCase for CartArticleAdapter"""

    def setUp(self):
        from plone.app.testing import TEST_USER_ID
        from plone.app.testing import setRoles
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_subclass(self):
        from collective.cart.core.adapter.cartarticle import CartArticleAdapter as BaseCartArticleAdapter
        from collective.cart.shopping.adapter.cartarticle import CartArticleAdapter
        self.assertTrue(issubclass(CartArticleAdapter, BaseCartArticleAdapter))
        from collective.cart.core.interfaces import ICartArticleAdapter as IBaseCartArticleAdapter
        from collective.cart.shopping.interfaces import ICartArticleAdapter
        self.assertTrue(issubclass(ICartArticleAdapter, IBaseCartArticleAdapter))

    def test_provides(self):
        from collective.cart.shopping.adapter.cartarticle import CartArticleAdapter
        from collective.cart.shopping.interfaces import ICartArticleAdapter
        self.assertEqual(getattr(CartArticleAdapter, 'grokcore.component.directive.provides'), ICartArticleAdapter)

    def create_cart_article(self, **kwargs):
        instance = createContentInContainer(self.portal, 'collective.cart.core.CartArticle', checkConstraints=False, **kwargs)
        modified(instance)
        return instance

    def test_gross_subtotal(self):
        from collective.cart.shopping.interfaces import ICartArticleAdapter
        instance = self.create_cart_article(id='1', gross=Money(Decimal('20.00'), 'EUR'), quantity=2)
        adapter = ICartArticleAdapter(instance)
        self.assertEqual(adapter.gross_subtotal, Money(Decimal('40.00'), 'EUR'))

        adapter.context.quantity = 0
        self.assertEqual(adapter.gross_subtotal, Money(Decimal('0.00'), 'EUR'))
