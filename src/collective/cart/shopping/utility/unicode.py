from Products.CMFPlone.utils import safe_unicode
from collective.cart.shopping.interfaces import IUnicodeUtility
from five import grok
from zope.interface import implements


class UnicodeUtility(grok.GlobalUtility):
    implements(IUnicodeUtility)

    def safe_unicode(self, value, encoding=None):
        """Returns unicode of value.

        :param value: Basestring
        :type value: basestring

        :param encoding: Character set
        :type encoding: str

        :rtype: unicode
        """
        if encoding is not None:
            return safe_unicode(value, encoding)
        return safe_unicode(value)

    def fullname(self, address, encoding=None):
        """Format full name

        :param address: Address information
        :type address: dictionary

        :param encoding: Character set
        :type encoding: str

        :rtype: unicode
        """
        return u'{} {}'.format(self.safe_unicode(address['first_name'], encoding=encoding),
            self.safe_unicode(address['last_name'], encoding=encoding))

    def address(self, address, encoding=None):
        """Format address

        :param address: Address information
        :type address: dictionary

        :param encoding: Character set
        :type encoding: str

        :rtype: unicode
        """
        return u"""{first_name} {last_name}  {organization}  {vat}
{street}
{post} {city}
{phone}
{email}
""".format(
            first_name=self.safe_unicode(address['first_name'], encoding=encoding),
            last_name=self.safe_unicode(address['last_name'], encoding=encoding),
            organization=self.safe_unicode(address['organization'], encoding=encoding),
            vat=self.safe_unicode(address['vat'], encoding=encoding),
            street=self.safe_unicode(address['street'], encoding=encoding),
            post=self.safe_unicode(address['post'], encoding=encoding),
            city=self.safe_unicode(address['city'], encoding=encoding),
            phone=self.safe_unicode(address['phone'], encoding=encoding),
            email=address['email'])
