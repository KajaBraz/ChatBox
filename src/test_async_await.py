import asyncio
import time


async def czekaj(ile):
    print(f"{time.time()} zaczynam czekanie {ile}")
    await asyncio.sleep(ile)
    print(f"{time.time()} po czekaniu {ile}")
    return ile


async def glowna_funkcja():
    print(f'{time.time()} start')
    f5 = czekaj(5)
    f2 = czekaj(2)
    f3 = czekaj(3)
    # t = await asyncio.create_task(f5)
    # print(time.time(), t)
    # asyncio.create_task(f2)
    # asyncio.create_task(f3)
    r = await asyncio.gather(f5, f2, f3, czekaj(1))
    print(r)
    print(f"{time.time()} czekam main")
    await asyncio.sleep(10)
    print(f'{time.time()} stop')


if __name__ == "__main__":
    asyncio.run(glowna_funkcja())
