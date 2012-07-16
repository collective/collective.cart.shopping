from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.shopping.interfaces import IInfoSchema
from five import grok
from plone.directives import form
from z3c.form import field


# class InfoForm(form.SchemaForm):
class InfoForm(form.Form):
    grok.context(IShoppingSiteRoot)
    # grok.context(Interface)
    grok.name('collective.cart.shopping.info.form.')
    grok.require('zope2.View')

    ignoreContext = True
    # schema = IInfoSchema
    fields = field.Fields(IInfoSchema)