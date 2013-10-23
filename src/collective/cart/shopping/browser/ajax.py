from Products.Five.browser import BrowserView
from collective.cart.shopping.interfaces import IArticleAdapter
from zExceptions import Forbidden
from zope.interface import implements

import json


class SelectSubarticle(BrowserView):
    """AJAX action to select subarticle"""

    def __call__(self):

        authenticator = self.context.restrictedTraverse('@@authenticator')
        if not authenticator.verify():
            raise Forbidden()

        form = self.request.form
        uuid = form.get('uuid')
        if uuid:
            adapter = IArticleAdapter(self.context)
            obj = adapter.get_object(UID=uuid)
            if obj:
                maximum = IArticleAdapter(obj).quantity_max()
                data = {'uuid': uuid, 'size': len(str(maximum)), 'maximum': maximum}

                self.request.response.setHeader('Content-Type', 'application/json')
                return json.dumps(data)
