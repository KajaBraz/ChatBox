import os
from pathlib import Path

import arsenic


async def creaate_session() -> arsenic.Session:
    session = await arsenic.start_session(arsenic.services.Geckodriver(),
                                          arsenic.browsers.Firefox(**{'moz:firefoxOptions': {'args': ['-headless']}}))
    absolute_path = os.path.join(Path.home(), 'GitProjects', 'ChatBox', 'javascript', 'index.html')
    await session.get(f'file:///{absolute_path}')
    return session


async def connect_user(username: str, chat: str, session: arsenic.Session) -> None:
    login_elem = await session.get_element('#login')
    chat_elem = await session.get_element('#findChat')
    await login_elem.clear()
    await chat_elem.clear()
    connect_button_elem = await session.get_element('#connectButton')
    await login_elem.send_keys(username)
    await chat_elem.send_keys(chat)
    await connect_button_elem.click()
