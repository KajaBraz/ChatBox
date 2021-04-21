from src.helper_functions import check_url


def test_check_url():
    correct_urls = ['/mychat/myloginqwertyuioplkjhgfdsaz', '/MyChat/MyLoginxcvbnm0987654321',
                    '/MyChat/MyLogin0olCnoRHyfTxvAh3TD09']
    wrong_urls = ['/mychat/¯\\_(ツ)_/¯/0olCnoRHyfTxvAh3TD0q', '/my_chat/my_login0olCnoRHyfTxvAh3TD0q',
                  '/chat_name/Login:)0olCnoRHyfTxvAh3TD0q', '/chat_name/MyLogin!0olCnoRHyfTxvAh3TD0q',
                  '/chatname/MyLogin@0olCnoRHyfTxvAh3TD0q', '/chatname?/MyLogin0olCnoRHyfTxvAh3TD0q',
                  '/MyChat/my login0olCnoRHyfTxvAh3TD0q', '/my chat/my login0olCnoRHyfTxvAh3TD0q',
                  '/pokój/mylogin0olCnoRHyfTxvAh3TD0q', 'mychat/mylogin0olCnoRHyfTxvAh3TD0q',
                  '/myChat/myLogin/0olCnoRHyfTxvAh3TD0q']
    assert all([check_url(url) for url in correct_urls])
    assert not any([check_url(url) for url in wrong_urls])
