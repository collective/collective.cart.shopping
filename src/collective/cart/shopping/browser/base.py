from collective.cart.shopping.interfaces import IShoppingSite


class Message(object):
    """Messages for shopping site root templates"""

    @property
    def message(self):
        name = '{}-message'.format(getattr(self, 'grokcore.component.directive.name'))
        brain = IShoppingSite(self.context).get_brain_for_text(name)
        if brain:
            return {
                'title': brain.Title,
                'description': brain.Description,
                'text': brain.getObject().CookedBody(),
            }
