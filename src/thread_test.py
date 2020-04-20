from time import sleep
from time import time
import threading


def fun1():
    time_start = time()
    for i in range(10):
        print("fun1", time() - time_start)
        sleep(1)


def fun2():
    time_start = time()
    for i in range(5):
        print("funkcja 2", time() - time_start)
        sleep(2)


if __name__ == "__main__":
    print("START")
    # # BEZ WATKOW
    # fun1()
    # fun2()

    # Z WATKAMI
    t1 = threading.Thread(target=fun1)
    t2 = threading.Thread(target=fun2)
    t1.start()
    t2.start()

    t1.join()
    t2.join()
    print("STOP")
