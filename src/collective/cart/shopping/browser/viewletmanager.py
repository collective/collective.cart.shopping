from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.base.viewletmanager import RepeatedViewletManager
from collective.cart.shopping.browser.interfaces import IOrderListingViewletManager
from collective.cart.shopping.interfaces import ICollapsedOnLoad
from collective.cart.shopping.interfaces import IOrder
from collective.cart.shopping.interfaces import IOrderAdapter
from zope.component import getUtility
from zope.interface import implements


class OrderListingViewletManager(RepeatedViewletManager):
    """Viewlet manager for order listing"""
    implements(IOrderListingViewletManager)
    template = ViewPageTemplateFile('viewletmanagers/order-listing.pt')

    def _orders(self):
        order = IOrderAdapter(self.context)
        return order.get_content_listing(IOrder, depth=0)

    def items(self):
        """Returns list of dictionary of orders

        :rtype: list
        """
        res = []
        workflow = getToolByName(self.context, 'portal_workflow')
        toLocalizedTime = self.context.restrictedTraverse('@@plone').toLocalizedTime
        for item in self._orders():
            obj = item.getObject()
            order = IOrderAdapter(obj)
            res.append({
                'id': item.getId(),
                'modified': toLocalizedTime(item.modified),
                'state_title': workflow.getTitleForStateOnType(item.review_state(), item.portal_type),
                'title': item.Title(),
                'url': item.getURL(),
                'order': order,
                'obj': obj,
            })
        return res

    def class_collapsible(self):
        """Returns styling values

        :rtype: str
        """
        utility = getUtility(ICollapsedOnLoad)
        if len(self.items()) == 1:
            return utility(collapsed=False)
        return utility()
