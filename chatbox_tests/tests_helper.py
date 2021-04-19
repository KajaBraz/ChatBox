import unittest

from src.helper_functions import check_url


class MyTestCase(unittest.TestCase):
    def test_check_url(self):
        correct_urls = ['/mychat/mylogin0olCnoRHyfTxvAh3TD0q', '/MyChat/MyLogin0olCnoRHyfTxvAh3TD0q']
        wrong_urls = ['/mychat/¯\_(ツ)_/¯/0olCnoRHyfTxvAh3TD0q', '/my_chat/my_login0olCnoRHyfTxvAh3TD0q',
                      '/chat_name/Login:)0olCnoRHyfTxvAh3TD0q', '/chat_name/MyLogin!0olCnoRHyfTxvAh3TD0q',
                      '/chatname/MyLogin@0olCnoRHyfTxvAh3TD0q', '/chatname?/MyLogin0olCnoRHyfTxvAh3TD0q',
                      '/MyChat/my login0olCnoRHyfTxvAh3TD0q', '/my chat/my login0olCnoRHyfTxvAh3TD0q',
                      '/pokój/mylogin0olCnoRHyfTxvAh3TD0q', 'mychat/mylogin0olCnoRHyfTxvAh3TD0q',
                      '/myChat/myLogin/0olCnoRHyfTxvAh3TD0q']
        correct = [check_url(url) for url in correct_urls]
        wrong = [check_url(url) for url in wrong_urls]
        for is_correct in correct:
            self.assertTrue(is_correct)
        for is_wrong in wrong:
            self.assertFalse(is_wrong)
