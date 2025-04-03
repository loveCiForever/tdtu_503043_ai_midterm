from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


def manhattan_dst(x1: int, y1: int, x2: int, y2: int) -> int:
    return int(abs(x1 - x2) + abs(y1 - y2))


def euclidean_dst(x1: int, y1: int, x2: int, y2: int) -> float:
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5
