from zope.i18nmessageid import MessageFactory


_ = MessageFactory("collective.cart.shopping")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
