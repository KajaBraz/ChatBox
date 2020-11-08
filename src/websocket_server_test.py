import asyncio
import websockets
import time


async def websocket_server(websocket, path):
    print(f"path = {path}")
    r = await websocket.recv()
    print(f"received {r}")
    await websocket.send("ok")
    print("response sent")


async def print_and_wait(t):
    await asyncio.sleep(t)
    print(f"sleep for {t} seconds; time = {time.time()}")


async def main():
    print(0)
    await asyncio.gather(print_and_wait(3), print_and_wait(2), print_and_wait(1))
    print(1)
    server = await websockets.serve(websocket_server, "localhost", 8877)
    print(2)
    await server.wait_closed()
    print(3)


if __name__ == "__main__":
    asyncio.run(main())

    # print(1)
    # asyncio.get_event_loop().run_until_complete(print_and_wait(3))
    # print(10)
    # asyncio.get_event_loop().run_until_complete(print_and_wait(2))
    # print(20)
    # asyncio.get_event_loop().run_until_complete(print_and_wait(1))
    # print(30)
    # server = websockets.serve(websocket_server, "localhost", 8877)
    # print(2)
    # asyncio.get_event_loop().run_until_complete(server)
    # print(3)
    # asyncio.get_event_loop().run_forever()
    # print(4)
