import asyncio
import os

import pytest
import pytest_asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from src import helper_functions, chatbox_websocket_server


def create_driver():
    options = Options()
    options.add_argument('--headless')  # don't use when you want to actually open and see the browser window
    # driver = webdriver.Firefox(options=options)
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
    relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
    absolute_path = os.path.abspath(relative_path)
    driver.get(f'file:///{absolute_path}')
    driver.implicitly_wait(10)
    return driver


class TestUser:
    def __init__(self):
        self.chat_room = helper_functions.generate_random_string(10)
        self.user_name = helper_functions.generate_random_string(10)
        self.driver: webdriver.Firefox = None


@pytest_asyncio.fixture
async def server():
    # config_path = '../chatbox_tests_config.json'
    # await chatbox_websocket_server.main(config_path, True)
    # yield
    # print('\nserver')

    config_path = '../chatbox_tests_config.json'
    data = helper_functions.read_config(config_path)
    address = data['address']['name']
    port = data['address']['port']
    chatbox_server = chatbox_websocket_server.Server(data)
    await chatbox_server.start(address, port)
    yield
    await chatbox_server.wait_stop()


@pytest_asyncio.fixture
async def user():
    client = TestUser()
    client.driver = create_driver()
    login_elem = client.driver.find_element(By.ID, 'login')
    chat_elem = client.driver.find_element(By.ID, 'findChat')
    connect_button_elem = client.driver.find_element(By.ID, 'connectButton')
    login_elem.send_keys(client.user_name)
    chat_elem.send_keys(client.chat_room)
    connect_button_elem.click()
    login_elem.clear()
    chat_elem.clear()

    yield client
    # folder = os.path.join(os.pardir, 'test_results', 'selenium_screenshots')
    # os.makedirs(folder, exist_ok=True)
    # screenshot_path = os.path.join(folder, f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png')
    # client.driver.get_screenshot_as_file(screenshot_path)
    # client.driver.get('https://www.google.com')
    await asyncio.sleep(2)
    client.driver.quit()


@pytest.mark.asyncio
async def test_first_connection(server, user):
    print('\ntest')
    header_elem = user.driver.find_element(By.ID, 'chatNameHeader')
    chat_list_elem = user.driver.find_element(By.ID, 'recentlyUsedChats')
    user_list_elem = user.driver.find_element(By.ID, 'activeUsers')
    await asyncio.sleep(2)
    # WebDriverWait(client.driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, 'chatUser').text != 'User 1')
    # WebDriverWait(client.driver, timeout=10).until(EC.text_to_be_present_in_element_value((By.CLASS_NAME, 'chatUser'), client.user_name))
    assert header_elem.text == user.chat_room
    assert chat_list_elem.find_element(By.ID, user.chat_room).text == user.chat_room
    assert user_list_elem.find_element(By.CLASS_NAME, 'chatUser').text == user.user_name


@pytest.mark.asyncio
async def test_sending_and_displaying_messages(server, user):
    new_message_box = user.driver.find_element(By.ID, 'newMessage')
    send_button = user.driver.find_element(By.ID, 'sendMessageButton')
    await asyncio.sleep(2)

    # SEND MESSAGES
    messages = [helper_functions.generate_random_string(15) for _ in range(5)]
    for message in messages:
        new_message_box.send_keys(message)
        send_button.click()
        await asyncio.sleep(2)

    # CHECK RECEIVED MESSAGES
    received_messages_box = user.driver.find_element(By.ID, 'receivedMessages')
    received_messages = [m.text for m in received_messages_box.find_elements(By.CLASS_NAME, 'messageText')]
    assert messages == received_messages


@pytest.mark.asyncio
async def test_recent_chats_display(server, user):
    chat_rooms = [helper_functions.generate_random_string(10) for _ in range(4)]
    chat_elem = user.driver.find_element(By.ID, 'findChat')
    connect_button_elem = user.driver.find_element(By.ID, 'connectButton')
    await asyncio.sleep(2)
    for chat_room in chat_rooms:
        chat_elem.send_keys(chat_room)
        connect_button_elem.click()
        await asyncio.sleep(1)
        chat_elem.clear()
    resulting_chat_names = [elem.text for elem in user.driver.find_elements(By.CLASS_NAME, 'availableChat')]
    assert chat_rooms[::-1] + [user.chat_room] == resulting_chat_names
    # todo fix: test passes and then hangs indefinitely


@pytest.mark.asyncio
async def test_active_users_display(server, user):
    def make_drivers(username):
        # todo move to a general function (connection) and use in other tests
        # todo fix the below version to open tabs instead of new windows
        # state.driver.execute_script("window.open('');")
        # state.driver.execute_script(f"window.open('file:///{state.absolute_path}', '_blank');")
        # state.driver.switch_to.window(state.driver.window_handles[-1])
        # state.driver.get(f'file:///{state.absolute_path}')

        new_dr = create_driver()

        login_elem = new_dr.find_element(By.ID, 'login')
        chat_elem = new_dr.find_element(By.ID, 'findChat')
        connect_button_elem = new_dr.find_element(By.ID, 'connectButton')
        login_elem.send_keys(username)
        chat_elem.send_keys(user.chat_room)
        connect_button_elem.click()
        return new_dr

    await asyncio.sleep(2)
    activer_users = user.driver.find_elements(By.CLASS_NAME, 'chatUser')
    assert {user.user_name} == {active_user.text for active_user in activer_users}

    new_users = {helper_functions.generate_random_string(10) for _ in range(4)}
    new_drivers = set()
    temp_users = {user.user_name}
    temp_drivers = {user.driver}

    for new_user in new_users:
        new_driver = make_drivers(new_user)
        new_drivers.add(new_driver)
        temp_users.add(new_user)
        temp_drivers.add(new_driver)
        await asyncio.sleep(2)
        temp_active_users = [{u.text for u in dr.find_elements(By.CLASS_NAME, 'chatUser')} for dr in temp_drivers]
        assert all(temp_users == displayed for displayed in temp_active_users)

    # todo, temporary to remove, use separate windows instead, not drivers
    for d in new_drivers:
        d.quit()


@pytest.mark.asyncio
async def test_messages_position(server, user):
    # CONNECT USER 2
    new_driver = create_driver()
    user2_login = helper_functions.generate_random_string(10)
    login_elem = new_driver.find_element(By.ID, 'login')
    chat_elem = new_driver.find_element(By.ID, 'findChat')
    connect_button_elem = new_driver.find_element(By.ID, 'connectButton')
    login_elem.send_keys(user2_login)
    chat_elem.send_keys(user.chat_room)
    connect_button_elem.click()

    # PREPARE MESSAGES USER1
    messages_user1 = [helper_functions.generate_random_string(15) for i in range(2)]
    new_message_box_user1 = user.driver.find_element(By.ID, 'newMessage')
    send_button_user1 = user.driver.find_element(By.ID, 'sendMessageButton')

    # PREPARE MESSAGES USER2
    messages_user2 = [helper_functions.generate_random_string(15) for i in range(2)]
    new_message_box_user2 = new_driver.find_element(By.ID, 'newMessage')
    send_button_user2 = new_driver.find_element(By.ID, 'sendMessageButton')

    # SEND MESSAGES
    new_message_box_user1.send_keys(messages_user1[0])
    send_button_user1.click()

    new_message_box_user2.send_keys(messages_user2[0])
    send_button_user2.click()

    new_message_box_user1.send_keys(messages_user1[1])
    send_button_user1.click()

    new_message_box_user2.send_keys(messages_user2[1])
    send_button_user2.click()

    # GATHER MESSAGES
    new_message_box_user1.click()
    new_message_box_user2.click()
    received_messages_user1 = user.driver.find_elements(By.CLASS_NAME, 'message')
    received_messages_user2 = new_driver.find_elements(By.CLASS_NAME, 'message')
    await asyncio.sleep(2)

    # CHECK MESSAGES STYLE
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


# @pytest.mark.asyncio
# async def test_previous_messages(server,user):
#     # todo enable to work without database
#     # works for displaying 10 messages on the client's connection
#
#     received_messages_box = client.driver.find_element_by_id('receivedMessages')
#
#     # USER 1 SENDS MESSAGES
#     messages = [helper_functions.generate_random_string(5) for i in range(20)]
#     new_msg_box = client.driver.find_element_by_id('newMessage')
#     send_button = client.driver.find_element_by_id('sendMessageButton')
#     for message in messages:
#         new_msg_box.send_keys(message)
#         send_button.click()
#         new_msg_box.clear()
#
#     # wait = WebDriverWait(client.driver, 10)
#     # wait.until(
#     #     lambda d: [m.text for m in received_messages_box.find_elements_by_class_name('messageText')] == messages,
#     #     f"Message not found - wait 1, {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#
#     # USER 2 CONNECTS
#     login_elem = client.driver.find_element_by_id('login')
#     chat_elem = client.driver.find_element_by_id('findChat')
#     connect_button_elem = client.driver.find_element_by_id('connectButton')
#     login_elem.send_keys(helper_functions.generate_random_string(5))
#     chat_elem.send_keys(client.chat_room)
#     connect_button_elem.click()
#
#     # wait.until(
#     #     lambda d: messages[10:] == [m.text for m in received_messages_box.find_elements_by_class_name('messageText')],
#     #     f"Message not found - wait 2, {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#
#     previous_messages_loaded_on_connection = received_messages_box.find_elements_by_class_name('messageText')
#     assert messages[10:] == [m.text for m in previous_messages_loaded_on_connection]
#
#     client.driver.execute_script("receivedMessages.scrollTo(0, -receivedMessages.offsetHeight)")
#     # wait.until(
#     #     lambda d: messages == [m.text for m in received_messages_box.find_elements_by_class_name('messageText')],
#     #     f"Message not found, wait 3 {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#     more_previous_messages_loaded_after_scoll = received_messages_box.find_elements_by_class_name('messageText')
#
#     assert messages == [m.text for m in more_previous_messages_loaded_after_scoll]

@pytest.mark.asyncio
async def test_adjust_number_of_displayed_messages(server, user):
    # works for max num of messgaes in messages box set to 20
    max_msgs_on_page_num = 20

    received_messages_box = user.driver.find_element(By.ID, 'receivedMessages')
    new_message_box = user.driver.find_element(By.ID, 'newMessage')
    send_button = user.driver.find_element(By.ID, 'sendMessageButton')
    await asyncio.sleep(2)

    messages = [helper_functions.generate_random_string(5) for _ in range(25)]
    for message in messages[:max_msgs_on_page_num]:
        new_message_box.send_keys(message)
        send_button.click()
        await asyncio.sleep(2)

    await asyncio.sleep(2)
    displayed_messages = received_messages_box.find_elements(By.CLASS_NAME, 'messageText')
    assert len(displayed_messages) == max_msgs_on_page_num
    assert messages[:max_msgs_on_page_num] == [m.text for m in displayed_messages]

    i_start = 1
    for message in messages[max_msgs_on_page_num:]:
        new_message_box.send_keys(message)
        send_button.click()
        await asyncio.sleep(2)
        displayed_messages = received_messages_box.find_elements(By.CLASS_NAME, 'messageText')
        await asyncio.sleep(1)
        assert len(displayed_messages) == max_msgs_on_page_num
        assert messages[i_start:i_start + max_msgs_on_page_num] == [m.text for m in displayed_messages]
        i_start += 1
        await asyncio.sleep(1)
    await asyncio.sleep(5)


@pytest.mark.asyncio
def test_send_and_open_link(server, user):
    message_1 = 'www.rai.it'
    message_2 = 'https://www.gazzetta.it/Calcio/Serie-A/Napoli/' \
                '04-05-2023/scudetto-napoli-campione-d-italia-la-terza-volta-4601354295987.shtml'
    new_message_box = user.driver.find_element_by_id('newMessage')
    send_button = user.driver.find_element_by_id('sendMessageButton')

    # SEND MESSAGES
    new_message_box.send_keys(message_1)
    send_button.click()
    new_message_box.send_keys(message_2)
    send_button.click()

    # CLICK LINKS
    messages = user.driver.find_elements_by_class_name('messageText')
    messages[-1].click()
    messages[-2].click()

    assert len(user.driver.window_handles) == 3

    # SEND MESSAGE
    message_3 = 'abc abc https://www.italia.it/it/sicilia/agrigento abc abc'
    new_message_box.send_keys(message_3)
    send_button.click()

    # CLICK LINKS
    a = user.driver.find_elements_by_tag_name('a')
    a[-1].click()

    assert len(user.driver.window_handles) == 4
