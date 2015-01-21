from Products.CMFCore.utils import getToolByName

import logging


PROFILE_ID = 'profile-collective.cart.shopping:default'


def reimport_rolemap(context, logger=None):
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


def reimport_propertiestool(context, logger=None):
    """Update propertiestool"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting propertiestool.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'propertiestool', run_dependencies=False, purge_old=False)


def reimport_catalog(context, logger=None):
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


def reimport_jsregistry(context, logger=None):
    """Reimport jsregistry"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting jsregistry.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'jsregistry', run_dependencies=False, purge_old=False)


def reimport_cssregistry(context, logger=None):
    """Reimport cssregistry"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting cssregistry.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'cssregistry', run_dependencies=False, purge_old=False)


def reimport_actions(context, logger=None):
    """Reimport actions"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting actions.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'actions', run_dependencies=False, purge_old=False)


def upgrade_14_to_15(context, logger=None):
    """Set article attribute: vat_rate"""
    if logger is None:
        logger = logging.getLogger(__name__)
    from collective.base.interfaces import IAdapter
    from collective.cart.shopping.interfaces import IArticle
    from zope.lifecycleevent import modified
    adapter = IAdapter(context)
    for brain in adapter.get_brains(IArticle, path=adapter.portal_path()):
        obj = brain.getObject()
        setattr(obj, 'vat_rate', obj.vat)
        modified(obj)

    from collective.cart.shipping.interfaces import IShippingMethod
    for brain in adapter.get_brains(IShippingMethod, path=adapter.portal_path()):
        obj = brain.getObject()
        setattr(obj, 'vat', obj.vat)
        obj.reindexObject(idxs=['vat'])


def make_subarticles_private(context, logger=None):
    """Make subarticles private if article with use_subarticle is private"""
    if logger is None:
        logger = logging.getLogger(__name__)
    from Products.CMFCore.WorkflowCore import WorkflowException
    from collective.base.interfaces import IAdapter
    from collective.cart.shopping.interfaces import IArticle
    from collective.cart.shopping.interfaces import IArticleAdapter
    from zope.lifecycleevent import modified

    wftool = getToolByName(context, 'portal_workflow')
    portal = IAdapter(context).portal()
    adapter = IAdapter(portal)
    particles = adapter.get_objects(IArticle, use_subarticle=True, review_state="published")
    action = 'hide'

    if particles:
        obj = particles[0]
        for trans in wftool.getTransitionsFor(obj):
            tid = trans['id']
            if tid == 'retract' or tid == 'reject':
                action = tid

    articles = adapter.get_objects(IArticle, use_subarticle=True, review_state="private")
    count = 0

    for article in articles:
        aadapter = IArticleAdapter(article)
        subarticles = aadapter.get_objects(IArticle, review_state="published")
        for subarticle in subarticles:
            subarticle_path = '/'.join(subarticle.getPhysicalPath())
            try:
                wftool.doActionFor(subarticle, action)
                modified(subarticle)
                message = 'Successfully hid subarticle: {}'.format(subarticle_path)
                logger.info(message)
                count += 1
            except WorkflowException:
                message = 'Already hidden subarticle? {}'.format(subarticle_path)
                logger.info(message)

    if count:
        message = 'There are total of {} subarticles hidden.'.format(count)
        logger.info(message)
