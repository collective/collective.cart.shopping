# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Testing import ZopeTestCase as ztc
from collective.cart.shopping.tests.base import FUNCTIONAL_TESTING
from datetime import date
from hexagonit.testing.browser import Browser
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.testing import layered
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
    browser = Browser(layer['app'])
    portal = layer['portal']
    # Update global variables within the tests.
    self.globs.update({
        'TEST_USER_NAME': TEST_USER_NAME,
        'TEST_USER_PASSWORD': TEST_USER_PASSWORD,
        'browser': browser,
        'portal': portal,
        'prink': prink,
    })
    ztc.utils.setupCoreSessions(layer['app'])
    browser.setBaseUrl(portal.absolute_url())

    browser.handleErrors = True
    portal.error_log._ignored_exceptions = ()

    setRoles(portal, TEST_USER_ID, ['Manager'])

    regtool = getToolByName(portal, 'portal_registration')

    member1 = 'member1'
    regtool.addMember(member1, member1)
    setRoles(portal, member1, ['Member'])
    self.globs['member1'] = member1

    member2 = 'member2'
    regtool.addMember(member2, member2)
    setRoles(portal, member2, ['Member'])
    self.globs['member2'] = member2

    self.globs['today'] = date.today()

    portal.manage_changeProperties(
        email_from_address='email@from.address', email_from_name='Email From Name')

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
        DocFileSuite('functional/browser.txt'),
        DocFileSuite('functional/manager-article.txt'),
        DocFileSuite('functional/manager-cart.txt'),
        DocFileSuite('functional/manager-order-confirmation.txt'),
        DocFileSuite('functional/manager-shipping.txt'),
        DocFileSuite('functional/manager-stock.txt'),
        DocFileSuite('functional/related-articles.txt'),
        DocFileSuite('functional/warn_number_of_images.txt')])
