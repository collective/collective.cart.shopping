from collective.cart.shopping.browser.base import Message

import mock
import unittest


class MessageTestCase(unittest.TestCase):
    """TestCase for Message"""

    def test_subclass(self):
        self.assertTrue(issubclass(Message, object))

    @mock.patch('collective.cart.shopping.browser.base.IShoppingSite')
    def test_message(self, IShoppingSite):
        instance = Message()
        self.assertIsNone(instance.message())

        instance.__name__ = mock.Mock()
        instance.__name__ = 'name'
        IShoppingSite().get_brain_for_text.return_value = None
        instance.context = mock.Mock()
        self.assertIsNone(instance.message())

        brain = mock.Mock()
        brain.Title = 'TITLE'
        brain.Description = 'DESCRIPTION'
        brain.getObject().CookedBody.return_value = 'TEXT'
        IShoppingSite().get_brain_for_text.return_value = brain
        self.assertEqual(instance.message(), {'text': 'TEXT', 'description': 'DESCRIPTION', 'title': 'TITLE'})
