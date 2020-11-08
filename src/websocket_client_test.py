import asyncio
import websockets


async def ws_client1():
    print("client 1")
    uri = "ws://localhost:8877/"
    async with websockets.connect(uri) as ws:
        await asyncio.sleep(10)
        await ws.send("test1")
        print("sent")
        r = await ws.recv()
        print(f"received {r}")

async def ws_client2():
    print("client 2")
    uri = "ws://localhost:8877/"
    wsc = await websockets.connect(uri)
    await asyncio.sleep(10)
    await wsc.send("test1")
    print("sent")
    r = await wsc.recv()
    print(f"received {r}")
    await wsc.close()

if __name__ == "__main__":
    # print(1)
    # asyncio.get_event_loop().run_until_complete(ws_client())
    # print(2)
    asyncio.run(ws_client2())
