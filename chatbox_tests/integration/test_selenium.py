import unittest
from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        # self.driver = webdriver.Firefox()

    def test_first_connection(self):
        # self.driver.get('http://13.58.103.103:11333/')
        self.driver.get('file:///C:/Users/Kaja/GitProjects/ChatBox/javascript/index.html')
        chat_room = 'NewChat'
        login = 'UserName'
        login_elem = self.driver.find_element_by_id('login')
        chat_elem = self.driver.find_element_by_id('findChat')
        connect_button_elem = self.driver.find_element_by_id('connectButton')
        header_elem = self.driver.find_element_by_id('chatNameHeader')
        chat_list_elem = self.driver.find_element_by_id('recentlyUsedChats')
        user_list_elem = self.driver.find_element_by_id('activeUsers')
        login_elem.send_keys('UserName')
        chat_elem.send_keys('NewChat')
        connect_button_elem.click()
        assert header_elem.text == chat_room
        assert chat_list_elem.find_element_by_id(chat_room).text == chat_room
        assert user_list_elem.find_element_by_class_name('chatUser').text == login

    def tearDown(self) -> None:
        self.driver.quit()
