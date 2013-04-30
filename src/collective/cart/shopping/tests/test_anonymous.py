# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Testing import ZopeTestCase as ztc
from collective.cart.shopping.tests.base import FUNCTIONAL_TESTING
from decimal import Decimal
from hexagonit.testing.browser import Browser
from moneyed import Money
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.testing import layered
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.lifecycleevent import modified
from zope.testing import renormalizing

import doctest
import manuel.codeblock
import manuel.doctest
import manuel.testing
import re
import transaction
import unittest

FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

CHECKER = renormalizing.RENormalizing([
    # Normalize the generated UUID values to always compare equal.
    (re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<UUID>'),
])


def prink(e):
    print eval('"""{0}"""'.format(str(e)))


def setUp(self):
    layer = self.globs['layer']
    portal = layer['portal']
    app = layer['app']
    browser = Browser(app)
    self.globs.update({
        'TEST_USER_NAME': TEST_USER_NAME,
        'TEST_USER_PASSWORD': TEST_USER_PASSWORD,
        'browser': browser,
        'portal': portal,
        'prink': prink,
    })
    ztc.utils.setupCoreSessions(app)
    browser.setBaseUrl(portal.absolute_url())
    browser.handleErrors = True
    portal.error_log._ignored_exceptions = ()
    setRoles(portal, TEST_USER_ID, ['Manager'])

    workflow = getToolByName(portal, 'portal_workflow')

    # Create Shop
    shop = createContentInContainer(portal, 'collective.cart.shopping.Shop', checkConstraints=False, title='Shöp')
    modified(shop)
    workflow.doActionFor(shop, 'publish')

    # Create Cart Container
    cart_container = createContentInContainer(shop, 'collective.cart.core.CartContainer', checkConstraints=False, id='cart-container')
    modified(cart_container)

    # Create Shipping Method Container
    shipping_method_container = createContentInContainer(shop, 'collective.cart.shipping.ShippingMethodContainer',
        checkConstraints=False, id='shipping-method-container')
    modified(shipping_method_container)

    # Add two shipping method
    shipping_method1 = shipping_method_container[shipping_method_container.invokeFactory('ShippingMethod', 'shippingmethod1',
        title='ShippingMethöd1', vat=24.0)]
    modified(shipping_method1)
    workflow.doActionFor(shipping_method1, 'publish')
    shipping_method2 = shipping_method_container[shipping_method_container.invokeFactory('ShippingMethod', 'shippingmethod2',
        title='ShippingMethöd2', vat=24.0)]
    modified(shipping_method2)
    workflow.doActionFor(shipping_method2, 'publish')

    self.globs['shippingmethod2_uuid'] = IUUID(shipping_method2)

    # Add Article
    article1 = createContentInContainer(shop, 'collective.cart.core.Article', checkConstraints=False, title='Ärticle1',
        money=Money(Decimal('12.40'), currency='EUR'), vat_rate=24.0, reducible_quantity=100, sku='SKÖ1', salable=True)
    modified(article1)
    workflow.doActionFor(article1, 'publish')

    # Add Stock
    stock1 = createContentInContainer(article1, 'collective.cart.stock.Stock', checkConstraints=False, title='Stöck1',
        stock=10)
    modified(stock1)

    # # Create shop folder
    # shop = portal[portal.invokeFactory('Folder', 'shop', title='Shöp')]
    # modified(shop)
    # workflow = getToolByName(portal, 'portal_workflow')
    # workflow.doActionFor(shop, 'publish')

    getUtility(IRegistry)['collective.cart.shopping.notification_cc_email'] = u'info@shop.com'

    # ## Setup MockMailHost
    from Products.CMFPlone.tests.utils import MockMailHost
    from Products.MailHost.interfaces import IMailHost
    from zope.component import getSiteManager
    portal._original_MailHost = portal.MailHost
    portal.MailHost = mailhost = MockMailHost('MailHost')
    sm = getSiteManager(context=portal)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(mailhost, provided=IMailHost)
    self.globs.update({
        'mailhost': portal.MailHost,
    })

    transaction.commit()


def DocFileSuite(testfile, flags=FLAGS, setUp=setUp, layer=FUNCTIONAL_TESTING):
    """Returns a test suite configured with a test layer.

    :param testfile: Path to a doctest file.
    :type testfile: str

    :param flags: Doctest test flags.
    :type flags: int

    :param setUp: Test set up function.
    :type setUp: callable

    :param layer: Test layer
    :type layer: object

    :rtype: `manuel.testing.TestSuite`
    """
    m = manuel.doctest.Manuel(optionflags=flags, checker=CHECKER)
    m += manuel.codeblock.Manuel()

    return layered(
        manuel.testing.TestSuite(m, testfile, setUp=setUp, globs=dict(layer=layer)),
        layer=layer)


def test_suite():
    return unittest.TestSuite([
        DocFileSuite('functional/anonymous.txt')])
