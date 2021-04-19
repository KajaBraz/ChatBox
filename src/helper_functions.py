def check_url(input: str) -> bool:
    range1 = range(48, 57)
    range2 = range(65, 90)
    range3 = range(97, 122)
    if input.count('/') != 2:
        return False
    input = input.replace('/', '')
    for ch in input:
        o = ord(ch)
        if o not in range1 and o not in range2 and o not in range3:
            return False
    return True
