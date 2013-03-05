from Products.CMFCore.utils import getToolByName
from Testing import ZopeTestCase as ztc
from decimal import Decimal
from moneyed import Money
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer
from plone.testing import z2
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import directlyProvides
from zope.lifecycleevent import modified
from zope.publisher.browser import TestRequest

import mock
import unittest


class CollectiveCartShoppingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""

        # Required by Products.CMFPlone:plone-content to setup defaul plone site.
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'Products.ATCountryWidget')

        # Load ZCML
        import collective.cart.shopping
        self.loadZCML(package=collective.cart.shopping)
        z2.installProduct(app, 'collective.cart.shopping')
        z2.installProduct(app, 'collective.cart.shipping')

    def setUpPloneSite(self, portal):
        """Set up Plone."""

        # Installs all the Plone stuff. Workflows etc. to setup defaul plone site.
        self.applyProfile(portal, 'Products.CMFPlone:plone')

        # Install portal content. Including the Members folder! to setup defaul plone site.
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')

        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.cart.shopping:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'collective.cart.shipping')
        z2.uninstallProduct(app, 'collective.cart.shopping')
        z2.uninstallProduct(app, 'ATCountryWidget')
        z2.uninstallProduct(app, 'Products.PythonScripts')


FIXTURE = CollectiveCartShoppingLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="CollectiveCartShoppingLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="CollectiveCartShoppingLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        ztc.utils.setupCoreSessions(self.layer['app'])
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def create_content(self, ctype, parent=None, **kwargs):
        if parent is None:
            parent = self.portal
        content = createContentInContainer(parent, ctype, checkConstraints=False, **kwargs)
        modified(content)
        return content

    def create_atcontent(self, ctype, parent=None, **kwargs):
        if parent is None:
            parent = self.portal
        content = parent[parent.invokeFactory(ctype, **kwargs)]
        content.reindexObject()
        return content

    def create_view(self, view, context=None):
        if context is None:
            context = self.portal
        request = TestRequest()
        directlyProvides(request, IAttributeAnnotatable)
        request.set = mock.Mock()
        return view(context, request)

    def create_viewlet(self, viewlet, context=None):
        if context is None:
            context = self.portal
        request = TestRequest()
        directlyProvides(request, IAttributeAnnotatable)
        request.set = mock.Mock()
        return viewlet(context, request, None, None)

    def decimal(self, value):
        return Decimal(value)

    def money(self, price, currency='EUR'):
        return Money(Decimal(price), currency)

    @property
    def ulocalized_time(self):
        return getToolByName(self.portal, 'translation_service').ulocalized_time


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
