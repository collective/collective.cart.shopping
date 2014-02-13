from collective.base.interfaces import IAdapter
from collective.behavior.sku import _
from collective.behavior.sku.interfaces import ISKU
from collective.cart.shopping.interfaces import IArticle
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from zope.interface import Invalid


class ValidateSKUUniqueness(SimpleFieldValidator):
    """Validate uniqueness of SKU"""

    def validate(self, value):
        super(ValidateSKUUniqueness, self).validate(value)

        if getattr(self.context, 'sku', u'') != value:
            adapter = IAdapter(self.context)
            brains = adapter.get_brains(IArticle, path=adapter.portal_path(), sku=value)

            if brains:
                raise Invalid(_(u'The SKU is already in use.'))


WidgetValidatorDiscriminators(ValidateSKUUniqueness, field=ISKU['sku'])
