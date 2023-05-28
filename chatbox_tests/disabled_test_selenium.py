import datetime
import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from src import helper_functions


class TestState:
    def __init__(self):
        self.driver: webdriver.Firefox = None
        self.chat_room = ''
        self.user_name = ''
        self.chat_elem = None
        self.connect_button_elem = None
        self.login_elem = None


def create_driver():
    options = Options()
    options.add_argument('--headless')  # don't use when you want to actually open and see the browser window
    driver = webdriver.Firefox(options=options)
    relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
    absolute_path = os.path.abspath(relative_path)
    driver.get(f'file:///{absolute_path}')
    driver.implicitly_wait(10)
    return driver


@pytest.fixture
def state():
    state = TestState()
    state.driver = create_driver()

    # USER'S CONNECTION
    state.user_name = helper_functions.generate_random_string(10)
    state.chat_room = helper_functions.generate_random_string(10)
    state.login_elem = state.driver.find_element_by_id('login')
    state.chat_elem = state.driver.find_element_by_id('findChat')
    state.connect_button_elem = state.driver.find_element_by_id('connectButton')
    state.login_elem.send_keys(state.user_name)
    state.chat_elem.send_keys(state.chat_room)
    state.connect_button_elem.click()

    yield state
    state.login_elem.clear()
    state.chat_elem.clear()
    screenshot_path = os.path.abspath(os.path.join(os.pardir, 'test_results', 'selenium_screenshots',
                                                   f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'))
    state.driver.get_screenshot_as_file(screenshot_path)
    state.driver.quit()


def test_first_connection(state: TestState):
    header_elem = state.driver.find_element_by_id('chatNameHeader')
    chat_list_elem = state.driver.find_element_by_id('recentlyUsedChats')
    user_list_elem = state.driver.find_element_by_id('activeUsers')
    assert header_elem.text == state.chat_room
    assert chat_list_elem.find_element_by_id(state.chat_room).text == state.chat_room
    assert user_list_elem.find_element_by_class_name('chatUser').text == state.user_name


def test_sending_and_displaying_messages(state: TestState):
    new_message_box = state.driver.find_element_by_id('newMessage')
    send_button = state.driver.find_element_by_id('sendMessageButton')

    # SENDING MESSAGES
    messages = [helper_functions.generate_random_string(15) for i in range(5)]
    for message in messages:
        new_message_box.send_keys(message)
        send_button.click()
    # CHECKING RECEIVED MESSAGES
    received_messages_box = state.driver.find_element_by_id('receivedMessages')
    received_messages = [m.text for m in received_messages_box.find_elements_by_class_name('messageText')]
    assert messages == received_messages


def test_recent_chats_display(state: TestState):
    chat_rooms = [helper_functions.generate_random_string(10) for i in range(4)]
    for chat_room in chat_rooms:
        state.chat_elem.send_keys(chat_room)
        state.connect_button_elem.click()
        state.chat_elem.clear()
    resulting_chat_names = [elem.text for elem in state.driver.find_elements_by_class_name('availableChat')]
    assert chat_rooms[::-1] + [state.chat_room] == resulting_chat_names


def test_active_users_display(state: TestState):
    def make_drivers(user):
        # todo fix the below version to open tabs instead of new windows
        # state.driver.execute_script("window.open('');")
        # state.driver.execute_script(f"window.open('file:///{state.absolute_path}', '_blank');")
        # state.driver.switch_to.window(state.driver.window_handles[-1])
        # state.driver.get(f'file:///{state.absolute_path}')

        new_dr = create_driver()

        login_elem = new_dr.find_element_by_id('login')
        chat_elem = new_dr.find_element_by_id('findChat')
        connect_button_elem = new_dr.find_element_by_id('connectButton')
        login_elem.send_keys(user)
        chat_elem.send_keys(state.chat_room)
        connect_button_elem.click()
        return new_dr

    activer_users = state.driver.find_elements_by_class_name('chatUser')
    assert {state.user_name} == {active_user.text for active_user in activer_users}

    new_users = {helper_functions.generate_random_string(10) for _ in range(4)}
    new_drivers = set()
    temp_users = {state.user_name}
    temp_drivers = {state.driver}

    for new_user in new_users:
        new_driver = make_drivers(new_user)
        new_drivers.add(new_driver)
        temp_users.add(new_user)
        temp_drivers.add(new_driver)
        temp_active_users = [{u.text for u in dr.find_elements_by_class_name('chatUser')} for dr in temp_drivers]
        assert all(temp_users == displayed for displayed in temp_active_users)

    # todo, temporary to remove, use separate windows instead, not drivers
    for d in new_drivers:
        d.quit()


def test_messages_position(state: TestState):
    # CONNECTION USER 2
    new_driver = create_driver()
    user2_login = helper_functions.generate_random_string(10)
    login_elem = new_driver.find_element_by_id('login')
    chat_elem = new_driver.find_element_by_id('findChat')
    connect_button_elem = new_driver.find_element_by_id('connectButton')
    login_elem.send_keys(user2_login)
    chat_elem.send_keys(state.chat_room)
    connect_button_elem.click()

    # PREPARING MESSAGES USER1
    messages_user1 = [helper_functions.generate_random_string(15) for i in range(2)]
    new_message_box_user1 = state.driver.find_element_by_id('newMessage')
    send_button_user1 = state.driver.find_element_by_id('sendMessageButton')

    # PREPARING MESSAGES USER2
    messages_user2 = [helper_functions.generate_random_string(15) for i in range(2)]
    new_message_box_user2 = new_driver.find_element_by_id('newMessage')
    send_button_user2 = new_driver.find_element_by_id('sendMessageButton')

    # SENDING MESSAGES
    new_message_box_user1.send_keys(messages_user1[0])
    send_button_user1.click()

    new_message_box_user2.send_keys(messages_user2[0])
    send_button_user2.click()

    new_message_box_user1.send_keys(messages_user1[1])
    send_button_user1.click()

    new_message_box_user2.send_keys(messages_user2[1])
    send_button_user2.click()

    # GATHERING OF THE MESSAGES
    new_message_box_user1.click()
    new_message_box_user2.click()
    received_messages_user1 = state.driver.find_elements_by_class_name('message')
    received_messages_user2 = new_driver.find_elements_by_class_name('message')

    # CHECKING MESSAGES STYLE
    messages_style_user1 = [m.get_attribute('style') for m in received_messages_user1]
    messages_style_user2 = [m.get_attribute('style') for m in received_messages_user2]

    assert all(['right' in messages_style_user1[i] for i in range(len(messages_style_user1)) if i % 2 == 0])
    assert all(['right' in messages_style_user2[i] for i in range(len(messages_style_user2)) if i % 2 == 1])
    assert all(['left' in messages_style_user1[i] for i in range(len(messages_style_user1)) if i % 2 == 1])
    assert all(['left' in messages_style_user2[i] for i in range(len(messages_style_user2)) if i % 2 == 0])

    # todo temporary, to remove, make seperate windows not drivers
    new_driver.quit()


def test_previous_messages(state: TestState):
    # works for displaying 10 messages on the client's connection

    received_messages_box = state.driver.find_element_by_id('receivedMessages')

    # USER 1 SENDS MESSAGES
    messages = [helper_functions.generate_random_string(5) for i in range(20)]
    new_msg_box = state.driver.find_element_by_id('newMessage')
    send_button = state.driver.find_element_by_id('sendMessageButton')
    for message in messages:
        new_msg_box.send_keys(message)
        send_button.click()
        new_msg_box.clear()

    wait = WebDriverWait(state.driver, 10)
    wait.until(
        lambda d: [m.text for m in received_messages_box.find_elements_by_class_name('messageText')] == messages,
        f"Message not found - wait 1, {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
    )

    # USER 2 CONNECTS
    state.login_elem.send_keys(helper_functions.generate_random_string(5))
    state.chat_elem.send_keys(state.chat_room)
    state.connect_button_elem.click()
    wait.until(
        lambda d: messages[10:] == [m.text for m in received_messages_box.find_elements_by_class_name('messageText')],
        f"Message not found - wait 2, {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
    )

    previous_messages_loaded_on_connection = received_messages_box.find_elements_by_class_name('messageText')
    assert messages[10:] == [m.text for m in previous_messages_loaded_on_connection]

    state.driver.execute_script("receivedMessages.scrollTo(0, -receivedMessages.offsetHeight)")
    wait.until(
        lambda d: messages == [m.text for m in received_messages_box.find_elements_by_class_name('messageText')],
        f"Message not found, wait 3 {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
    )
    more_previous_messages_loaded_after_scoll = received_messages_box.find_elements_by_class_name('messageText')

    assert messages == [m.text for m in more_previous_messages_loaded_after_scoll]


def test_adjust_number_of_displayed_messages(state: TestState):
    # works for max num of messgaes in messages box set to 20
    max_msgs_on_page_num = 20

    received_messages_box = state.driver.find_element_by_id('receivedMessages')
    new_message_box = state.driver.find_element_by_id('newMessage')
    send_button = state.driver.find_element_by_id('sendMessageButton')

    messages = [helper_functions.generate_random_string(5) for x in range(25)]
    for message in messages[:max_msgs_on_page_num]:
        new_message_box.send_keys(message)
        send_button.click()

    displayed_messages = received_messages_box.find_elements_by_class_name('messageText')
    assert len(displayed_messages) == max_msgs_on_page_num
    assert messages[:max_msgs_on_page_num] == [m.text for m in displayed_messages]

    i_start = 1
    for message in messages[max_msgs_on_page_num:]:
        new_message_box.send_keys(message)
        send_button.click()
        displayed_messages = received_messages_box.find_elements_by_class_name('messageText')
        assert len(displayed_messages) == max_msgs_on_page_num
        assert messages[i_start:i_start + max_msgs_on_page_num] == [m.text for m in displayed_messages]
        i_start += 1


def test_send_and_open_link(state: TestState):
    message_1 = 'www.rai.it'
    message_2 = 'https://www.gazzetta.it/Calcio/Serie-A/Napoli/' \
                '04-05-2023/scudetto-napoli-campione-d-italia-la-terza-volta-4601354295987.shtml'
    new_message_box = state.driver.find_element_by_id('newMessage')
    send_button = state.driver.find_element_by_id('sendMessageButton')

    # SEND MESSAGES
    new_message_box.send_keys(message_1)
    send_button.click()
    new_message_box.send_keys(message_2)
    send_button.click()

    # CLICK LINKS
    messages = state.driver.find_elements_by_class_name('messageText')
    messages[-1].click()
    messages[-2].click()

    assert len(state.driver.window_handles) == 3

    # SEND MESSAGE
    message_3 = 'abc abc https://www.italia.it/it/sicilia/agrigento abc abc'
    new_message_box.send_keys(message_3)
    send_button.click()

    # CLICK LINKS
    a = state.driver.find_elements_by_tag_name('a')
    a[-1].click()

    assert len(state.driver.window_handles) == 4
