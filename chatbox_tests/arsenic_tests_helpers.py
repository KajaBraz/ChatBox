import asyncio

import arsenic

from server_http.endpoints import app


async def creaate_session(chat_name: str = '', headless: bool = True) -> arsenic.Session:
    chat_in_lint = f'chat/{chat_name}'
    args = {'moz:firefoxOptions': {'args': ['-headless']}} if headless else {}
    session = await arsenic.start_session(arsenic.services.Geckodriver(), arsenic.browsers.Firefox(**args))
    await session.get(f'http://localhost:5000/{chat_in_lint}')
    await session.wait_for_element(20, '.gridContainer')
    return session


async def connect_user(session: arsenic.Session, username: str, chat: str = '') -> None:
    login_elem = await session.get_element('#login')
    chat_elem = await session.get_element('#findChat')
    await login_elem.clear()
    await login_elem.send_keys(username)
    if chat:
        await chat_elem.clear()
        await chat_elem.send_keys(chat)
    connect_button_elem = await session.get_element('#connectButton')
    await connect_button_elem.click()


def run_http_server():
    app.run()
