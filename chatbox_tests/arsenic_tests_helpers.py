import asyncio

import arsenic

from server_http.endpoints import app


async def creaate_session(chat_name='') -> arsenic.Session:
    session = await arsenic.start_session(arsenic.services.Geckodriver(),
                                          arsenic.browsers.Firefox(**{'moz:firefoxOptions': {'args': ['-headless']}}))
    await session.get(f'http://localhost:5000/{chat_name}')
    await asyncio.sleep(2)
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


def run_http_server():
    app.run()
