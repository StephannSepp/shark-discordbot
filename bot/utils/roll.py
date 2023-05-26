import random


def roll_under(max_n: int, x:int) -> int:
    """ Roll single time and get under x. """
    return random.randint(0, max_n) <= x


def roll_over(max_n: int, x:int) -> int:
    """ Roll single time and get over x. """
    return random.randint(0, max_n) > x


def rolls_lowest(times: int, max_n: int) -> int:
    """ Roll x times and keep the lowest. """
    lst = random.choices(range(0,max_n), k=times)
    return min(lst)


def rolls_highest(times: int, max_n: int) -> int:
    """ Roll x times and keep the highest. """
    lst = random.choices(range(0,max_n), k=times)
    return max(lst)


def rolls_under(times: int, max_n: int, x: int) -> int:
    """ Roll a number of times and get amount under x. """
    lst = random.choices(range(0,max_n), k=times)
    return sum(map(lambda e : e <= x, lst))


def rolls_over(times: int, max_n: int, x: int) -> int:
    """ Roll a number of times and get amount over x. """
    lst = random.choices(range(0,max_n), k=times)
    return sum(map(lambda e : e > x, lst))


def rolls_sum(times: int, max_n: int) -> int:
    """ Roll a number of times and get the sum. """
    lst = random.choices(range(0,max_n), k=times)
    return sum(lst)
