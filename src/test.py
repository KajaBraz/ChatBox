def fun(a):
    print("start!")
    i = 0
    while i < a:
        # print(f'przed yield {i}')
        yield i
        # print(f'po yield {i}')
        i += 1
    print("stop!")


def fun2():
    x = yield 1
    y = yield x
    yield y


def fun3(a):
    i = 0
    while i < a:
        r = yield i
        if r:
            i += r
        else:
            i += 1


if __name__ == "__main__":
    g3 = fun3(100)
    print(g3.send(None))
    print(next(g3))
    print(g3.send(None))
    print(g3.send(10))
    print(g3.send(20))
    print(next(g3))
    print(g3.send(2))
    print(g3.send(-1))
    print(g3.send(60))
    for i in g3:
        print("i", i)


    # g2 = fun2()
    # print(g2.send(None))
    # print(g2.send(20))
    # print(g2.send(30))

    # g = fun(3)
    # print(next(g))
    # print(next(g))
    # print(next(g))
    # print(next(g))

    # g = fun(3)
    # print(11)
    # print(g.send(None))
    # print(g.send(1))
    # print(g.send(1))

    # g = list(fun(10))
    # print(f"g = {g}")
    # for i in g:
    #     print(f"generator {i}")
    # print("pauza")
    # for i in g:
    #     print(f"generator {i}")
    # print("stop")
