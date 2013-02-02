from Products.CMFCore.utils import getToolByName

import logging


PROFILE_ID = 'profile-collective.cart.shopping:default'


def update_rolemap(context, logger=None):
    """Update rolemap"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting rolemap.')
    setup.runImportStepFromProfile(PROFILE_ID, 'rolemap', run_dependencies=False, purge_old=False)


def reimport_typeinfo(context, logger=None):
    """Update typeinfo"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting typeinfo.')
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo', run_dependencies=False, purge_old=False)


update_typeinfo = reimport_typeinfo


def update_propertiestool(context, logger=None):
    """Update propertiestool"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting propertiestool.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'propertiestool', run_dependencies=False, purge_old=False)


def update_catalog(context, logger=None):
    """Update catalog"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting catalog.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'catalog', run_dependencies=False, purge_old=False)
    catalog = getToolByName(context, 'portal_catalog')
    logger.info('Clearing, finding and rebuilding catalog.')
    catalog.clearFindAndRebuild()


def upgrade_6_to_7(context, logger=None):
    """Update use_subarticle attribute for Article."""
    from collective.cart.shopping.interfaces import IArticle
    from zope.lifecycleevent import modified

    if logger is None:
        logger = logging.getLogger(__name__)

    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(Language="all", object_provides=IArticle.__identifier__):
        if brain.use_subarticle is None:
            obj = brain.getObject()
            obj.use_subarticle = False
            modified(obj)


def reimport_viewlets(context, logger=None):
    """Update viewlets"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting viewlets.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'viewlets', run_dependencies=False, purge_old=False)


def reimport_registry(context, logger=None):
    """Reimport registry"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting registry.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'plone.app.registry', run_dependencies=False, purge_old=False)


def reimport_cssregistry(context, logger=None):
    """Reimport cssregistry"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting cssregistry.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'cssregistry', run_dependencies=False, purge_old=False)


update_viewlets = reimport_viewlets


def reimport_actions(context, logger=None):
    """Reimport actions"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting actions.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'actions', run_dependencies=False, purge_old=False)
