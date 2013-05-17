from collective.cart.shopping.interfaces import ICollapsedOnLoad
from zope.interface import implements


class CollapsedOnLoad(object):
    implements(ICollapsedOnLoad)

    def __call__(self, collapsed=True):
        if collapsed:
            return 'collapsible collapsedOnLoad'
        return 'collapsible'
