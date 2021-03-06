from Testing import ZopeTestCase as ztc
from collective.cart.shopping.tests.base import FUNCTIONAL_TESTING
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

FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.REPORT_NDIFF | doctest.REPORT_ONLY_FIRST_FAILURE

CHECKER = renormalizing.RENormalizing([
    # Normalize the generated UUID values to always compare equal.
    (re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<UUID>'),
])


def setUp(self):
    layer = self.globs['layer']
    browser = Browser(layer['app'])
    portal = layer['portal']
    # Update global variables within the tests.
    self.globs.update({
        'TEST_USER_NAME': TEST_USER_NAME,
        'TEST_USER_PASSWORD': TEST_USER_PASSWORD,
        'portal': portal,
        'browser': browser,
    })
    ztc.utils.setupCoreSessions(layer['app'])
    browser.setBaseUrl(portal.absolute_url())

    browser.handleErrors = True
    portal.error_log._ignored_exceptions = ()

    setRoles(portal, TEST_USER_ID, ['Manager'])

    # Set the site back in English mode to make testing easier.
    portal.portal_languages.manage_setLanguageSettings('en', ['en', 'fi'])

    # Set title and description for the plone site.
    portal.manage_changeProperties(title='Luonnonsuojelukauppa', description='Suomen Luonnonsuojelun Tuki Oy')

    # Make portal shipping site.
    from collective.cart.core.interfaces import IShoppingSiteRoot
    from zope.interface import alsoProvides
    alsoProvides(portal, IShoppingSiteRoot)
    portal.reindexObject(idxs=['object_provides'])

    from plone.dexterity.utils import createContentInContainer
    from zope.lifecycleevent import modified

    container = createContentInContainer(portal, 'collective.cart.core.CartContainer',
        id='cart-container', title='Cart Container', checkConstraints=False)
    modified(container)

    container = createContentInContainer(portal, 'collective.cart.shipping.ShippingMethodContainer',
        id='shipping-methods', title=u'Shipping Methods', checkConstraints=False)
    modified(container)

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
    return unittest.TestSuite([DocFileSuite('functional/manager-billing-and-shipping.txt')])
