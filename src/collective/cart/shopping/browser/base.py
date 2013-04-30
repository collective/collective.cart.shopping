from collective.cart.shopping.interfaces import IShoppingSite


class Message(object):
    """Messages for shopping site root"""

    def message(self, name=None):
        name = name or getattr(self, '__name__', None)
        if name is not None:
            name = '{}-message'.format(name)
            brain = IShoppingSite(self.context).get_brain_for_text(name)
            if brain:
                return {
                    'title': brain.Title,
                    'description': brain.Description,
                    'text': brain.getObject().CookedBody(),
                }
