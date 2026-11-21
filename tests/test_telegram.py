import unittest
from telegram_service import authorized,menu
class TelegramTests(unittest.TestCase):
    def msg(self,user=42,chat=42,kind='private'):
        return {'from':{'id':user},'chat':{'id':chat,'type':kind}}
    def test_private_defaults(self):self.assertTrue(authorized(self.msg(),{'42'},set()))
    def test_wrong_sender(self):self.assertFalse(authorized(self.msg(user=13),{'42'},set()))
    def test_group_denied_by_default(self):self.assertFalse(authorized(self.msg(chat=-1,kind='group'),{'42'},set()))
    def test_explicit_group(self):self.assertTrue(authorized(self.msg(chat=-1,kind='group'),{'42'},{'-1'}))
    def test_no_users(self):self.assertFalse(authorized(self.msg(),set(),{'42'}))
    def test_menu(self):self.assertEqual(menu()['inline_keyboard'][0][0]['callback_data'],'/preis')
