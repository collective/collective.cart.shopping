import mock
import unittest


class MessageTestCase(unittest.TestCase):

    @mock.patch('collective.cart.shopping.browser.base.IShoppingSite')
    def test_message(self, IShoppingSite):
        from collective.cart.shopping.browser.base import Message
        IShoppingSite().get_brain_for_text.return_value = None
        instance = Message()
        setattr(instance, 'grokcore.component.directive.name', 'name')
        setattr(instance, 'context', mock.Mock())
        self.assertIsNone(instance.message)

        brain = mock.Mock()
        brain.Title = 'TITLE'
        brain.Description = 'DESCRIPTION'
        brain.getObject().CookedBody.return_value = 'TEXT'
        IShoppingSite().get_brain_for_text.return_value = brain
        self.assertEqual(instance.message, {'text': 'TEXT', 'description': 'DESCRIPTION', 'title': 'TITLE'})
