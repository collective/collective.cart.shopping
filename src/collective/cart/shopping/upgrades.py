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


def update_typeinfo(context, logger=None):
    """Update typeinfo"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting typeinfo.')
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo', run_dependencies=False, purge_old=False)


def upgrade_1_to_2(context, logger=None):
    """Migrate SubArticle into Article."""
    from Acquisition import aq_inner
    from Acquisition import aq_parent
    from Products.CMFPlone.utils import safe_unicode
    from collective.behavior.discount.interfaces import IDiscount
    from collective.behavior.size.interfaces import ISize
    from collective.behavior.stock.interfaces import IStock
    from collective.behavior.vat.interfaces import IVAT
    from collective.cart.shopping.interfaces import IArticle
    from collective.cart.shopping.interfaces import ISubArticle
    from plone.dexterity.utils import createContentInContainer
    from zope.lifecycleevent import modified

    if logger is None:
        logger = logging.getLogger(__name__)

    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(Language="all", object_provides=ISubArticle.__identifier__):
        obj = brain.getObject()
        parent = aq_parent(aq_inner(obj))
        discount = IDiscount(obj)
        size = ISize(obj)
        oid = brain.id
        title = brain.Title
        items = {
            'id': oid,
            'description': brain.Description,
            'sku': brain.sku,
            'salable': brain.salable,
            'price': obj.price,
            'money': brain.money,
            'discount_enabled': discount.discount_enabled,
            'discount_price': discount.discount_price,
            'discount_money': discount.discount_money,
            'discount_start': discount.discount_start,
            'discount_end': discount.discount_end,
            'reducible_quantity': IStock(obj).reducible_quantity,
            'vat': IVAT(obj).vat,
            'weight': size.weight,
            'width': size.width,
            'height': size.height,
            'depth': size.depth,
        }

        path = '/'.join(obj.getPhysicalPath())
        logger.info('Deleting SubArticle at path: {}'.format(path))
        del parent[oid]

        logger.info('Creating Article to path: {}'.format(path))
        article = createContentInContainer(
            parent, 'collective.cart.core.Article',
            checkConstraints=False, **items)
        article.title = title
        modified(article)

    for brain in catalog(Language="all", object_provides=IArticle.__identifier__):
        obj = brain.getObject()
        if not isinstance(obj.title, unicode):
            logger.info('Setting unicode title to {}.'.format('/'.join(obj.getPhysicalPath())))
            obj.title = safe_unicode(obj.title)
            modified(obj)


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


def update_viewlets(context, logger=None):
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
