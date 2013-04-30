from collective.behavior.price.interfaces import ICurrency
from collective.behavior.vat.interfaces import IAdapter as IVATAdapter
from collective.cart.core.adapter.order import OrderAdapter as BaseOrderAdapter
from collective.cart.shipping.interfaces import IOrderShippingMethod
from collective.cart.shopping.interfaces import IArticle
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import ICustomerInfo
from collective.cart.shopping.interfaces import IOrder
from collective.cart.shopping.interfaces import IOrderAdapter
from collective.cart.shopping.interfaces import IOrderArticle
from collective.cart.shopping.interfaces import IOrderArticleAdapter
from collective.cart.shopping.interfaces import IShoppingSite
from collective.cart.shopping.interfaces import IUnicodeUtility
from moneyed import Money
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements


class OrderAdapter(BaseOrderAdapter):
    """Adapter for content type: collective.cart.core.Order"""

    adapts(IOrder)
    implements(IOrderAdapter)

    def articles(self):
        """Returns list of dictionary of order articles

        :rtype: list
        """
        res = []
        utility = getUtility(IUnicodeUtility)
        shopping_site = IShoppingSite(self.context)
        vat_adapter = IVATAdapter(self.context)
        for item in self.get_content_listing(IOrderArticle):
            obj = item.getObject()
            order_article_adapter = IOrderArticleAdapter(obj)
            gross_subtotal = order_article_adapter.gross_subtotal()
            items = {
                'description': utility.safe_unicode(item.Description()),
                'gross': item.gross,
                'gross_subtotal': gross_subtotal,
                'locale_gross_subtotal': shopping_site.format_money(gross_subtotal),
                'image_url': None,
                'obj': obj,
                'quantity': item.quantity,
                'sku': item.sku,
                'title': utility.safe_unicode(item.Title()),
                'url': None,
                'vat_rate': vat_adapter.percent(item.vat_rate),
                'id': item.getId(),
            }
            orig_article = shopping_site.get_object(IArticle, path=shopping_site.portal_path(), UID=item.getId())
            if orig_article:
                items['url'] = orig_article.absolute_url()
                items['image_url'] = IArticleAdapter(orig_article).image_url()
            res.append(items)
        return res

    def articles_total(self):
        """Returns total money of articles

        :rtype: moneyed.Money
        """
        registry = getUtility(IRegistry)
        currency = registry.forInterface(ICurrency).default_currency
        res = Money(0.00, currency=currency)
        for item in self.articles():
            res += item['gross_subtotal']
        return res

    def shipping_method(self):
        """Returns brain of shipping method"""
        return self.get_brain(IOrderShippingMethod, depth=1, unrestricted=True)

    def locale_shipping_method(self):
        """Returns dictionary of shipping method containing localized cost of it"""
        shipping_method = self.shipping_method()
        if shipping_method:
            return {
                'gross': IShoppingSite(self.context).format_money(shipping_method.gross),
                'is_free': shipping_method.gross.amount == 0.0,
                'title': shipping_method.Title,
                'vat_rate': shipping_method.vat_rate,
            }

    def total(self):
        total = self.articles_total()
        shipping_method = self.shipping_method()
        if shipping_method and shipping_method.gross:
            total += shipping_method.gross
        return total

    def get_address(self, name):
        """Return brain of address by name

        :param name: 'billing' or 'shipping'
        :type name: str
        """
        if name == 'shipping' and self.context.billing_same_as_shipping:
            name = 'billing'
        return self.get_brain(ICustomerInfo, depth=1, id=name)
