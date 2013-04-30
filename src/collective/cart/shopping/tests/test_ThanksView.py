# -*- coding: utf-8 -*-
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.browser.interfaces import IThanksView
from collective.cart.shopping.browser.template import ThanksView
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.tests.base import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.interface import alsoProvides

import mock


class ThanksViewTestCase(IntegrationTestCase):
    """TestCase for ThanksView"""

    def test_subclass(self):
        from collective.cart.shopping.browser.template import CheckOutView
        self.assertTrue(issubclass(ThanksView, CheckOutView))
        from collective.cart.shopping.browser.interfaces import ICheckOutView
        self.assertTrue(issubclass(IThanksView, ICheckOutView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(ThanksView)
        self.assertTrue(verifyObject(IThanksView, instance))

    def test_template(self):
        instance = self.create_view(ThanksView)
        self.assertEqual(instance.template.filename.split('/')[-1], 'thanks.pt')

    # @mock.patch('plone.protect.authenticator.AuthenticatorView.verify')
    # @mock.patch('collective.cart.shopping.browser.template.getToolByName')
    # @mock.patch('collective.cart.shopping.browser.template.IStatusMessage')
    # def test_update(self, IStatusMessage, getToolByName, verify):
    #     from collective.behavior.stock.interfaces import IStock
    #     instance = self.create_view(ThanksView)

    #     adapter = IShoppingSite(self.portal)
    #     session = adapter.getSessionData(create=True)
    #     session.set('collective.cart.core', {})
    #     address = {
    #         'city': 'CITY',
    #         'email': 'fist.last@email.com',
    #         'first_name': 'FIRST',
    #         'last_name': 'LAST',
    #         'phone': 'PHONE',
    #         'street': 'STREET',
    #     }
    #     adapter.update_cart('billing', address)
    #     adapter.update_cart('shipping', address)

    #     self.portal.absolute_url = mock.Mock(return_value='portal_url')
    #     verify.return_value = False
    #     from zExceptions import Forbidden
    #     with self.assertRaises(Forbidden):
    #         instance.update()

    #     verify.return_value = True
    #     self.assertEqual(instance.update(), 'portal_url/@@order-confirmation')

    #     instance.request.form = {'form.buttons.back': True}
    #     self.assertEqual(instance.update(), 'portal_url/@@billing-and-shipping')

    #     alsoProvides(self.portal, IShoppingSiteRoot)
    #     container = self.create_content('collective.cart.core.CartContainer', id='cart-container')
    #     article = self.create_content('collective.cart.core.Article', id='article', money=self.money('12.40'), vat_rate=24.0)
    #     self.create_content('collective.cart.stock.Stock', article, stock=10)
    #     behavior = IStock(article)
    #     self.assertEqual(behavior.stock, 10)

    #     uuid = IUUID(article)
    #     adapter.update_cart('articles', {uuid: {'id': uuid, 'quantity': 2, 'vat_rate': 24.0}})
    #     instance.request.form = {'form.buttons.ConfirmOrder': True}

    #     self.assertIsNone(instance.update())
    #     getToolByName().doActionFor.assert_called_with(container['1'], 'ordered')
    #     self.assertEqual(instance.cart_id, '1')
    #     self.assertEqual(behavior.stock, 8)

    #     confirmation_terms_message = self.create_atcontent('Folder', id='confirmation-terms-message')
    #     self.create_atcontent('Document', confirmation_terms_message, id='en')
    #     self.assertEqual(instance.update(), 'portal_url/@@order-confirmation')
    #     IStatusMessage().addStatusMessage.assert_called_with(u"need_to_accept_terms", type='info')
