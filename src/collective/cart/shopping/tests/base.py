from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from collective.cart.core.tests.base import IntegrationTestCase as BaseIntegrationTestCase
from decimal import Decimal
from moneyed import Money
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.interface import directlyProvides
from zope.publisher.browser import TestRequest

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


class IntegrationTestCase(BaseIntegrationTestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    def create_multiadapter(self, interface, context=None, obj=None):
        if context is None:
            context = self.portal
        if obj is None:
            request = TestRequest()
            directlyProvides(request, IAttributeAnnotatable)
            obj = request
        return getMultiAdapter((context, obj), interface)

    def decimal(self, value):
        return Decimal(value)

    def money(self, price, currency='EUR'):
        return Money(Decimal(price), currency)

    def toLocalizedTime(self):
        return self.portal.restrictedTraverse('@@plone').toLocalizedTime(DateTime())


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
