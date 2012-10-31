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
    setup.runImportStepFromProfile(
        'profile-collective.cart.shopping:default', 'typeinfo', run_dependencies=False, purge_old=False)


def upgrade_1_to_2(context, logger=None):
    """Migrate SubArticle into Article."""
    from Acquisition import aq_inner
    from Acquisition import aq_parent
    from collective.behavior.discount.interfaces import IDiscount
    from collective.behavior.size.interfaces import ISize
    from collective.behavior.stock.interfaces import IStock
    from collective.behavior.vat.interfaces import IVAT
    from collective.cart.shopping.interfaces import ISubArticle
    from plone.dexterity.utils import createContentInContainer
    from zope.lifecycleevent import modified

    if logger is None:
        logger = logging.getLogger(__name__)

    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(object_provides=ISubArticle.__identifier__):
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

        del parent[oid]

        article = createContentInContainer(
            parent, 'collective.cart.core.Article',
            checkConstraints=False, **items)
        article.title = title
        modified(article)
