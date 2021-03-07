import asyncio
import websockets
from src.enums import JsonFields, MessageTypes
from src.my_json import to_json


async def client(address,port,message, chat_name, user_name):
    url = f'ws://{address}:{port}/{chat_name}/{user_name}'
    ws = await websockets.connect(url)
    json_mess = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                 JsonFields.MESSAGE_VALUE: message,
                 JsonFields.MESSAGE_DESTINATION: chat_name,
                 JsonFields.MESSAGE_SENDER: user_name}
    print(json_mess)
    await ws.send(to_json(json_mess))
    r = await ws.recv()
    print(r)
    # await ws.close()
    return r


async def main():
    await client('localhost',11000,'ciao belli!','psiaki','flavia')
    await client('localhost',11000,'ciao ciao ciao','psiaki','pino')


if __name__ == '__main__':
    res=asyncio.run(main())
    print('RES', res)
