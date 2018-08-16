#!/bin/env python3

import random
from collections import Counter

NUM_ROWS = 8
NUM_COLS = 8

DIRECTIONS = ['N', 'W', 'S', 'E']
N, W, S, E = DIRECTIONS

class PosRobot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

POS_ROBOT = PosRobot(0, 0) # Top left corner.

DICT_DIRECTIONS = {DIR : 0.0 for DIR in DIRECTIONS}

matrix = [[DICT_DIRECTIONS]*NUM_COLS for _ in range(NUM_ROWS)]

def is_robot_locotion(x, y):
    return x == POS_ROBOT.x and y == POS_ROBOT.y

def read_sensor():

    def get_circle_dist_from_robot(tiles):
        xs = range(POS_ROBOT.x - tiles, POS_ROBOT.x + tiles + 1)
        ys = range(POS_ROBOT.y - tiles, POS_ROBOT.y + tiles + 1)

        def not_max_or_min(x, y):
            x_not_max_or_min = x not in [min(xs), max(xs)]
            y_not_may_or_min = y not in [min(ys), max(ys)]
            return x_not_max_or_min and y_not_may_or_min

        def less_than_zero(x, y):
            return x < 0 or y < 0

        def invalid_coords(x,y):
            return any([
                not_max_or_min(x,y),
                less_than_zero(x,y),
                is_robot_locotion(x,y),
            ])

        tiles = []
        for y in ys:
            for x in xs:
                if not invalid_coords(x,y):
                    tiles.append((x,y))
        return tiles

    Ls1 = get_circle_dist_from_robot(1)
    Ls2 = get_circle_dist_from_robot(2)

    prob_Ls1_upper = 0.1 + 0.05 * len(Ls1)
    prob_Ls2_upper = prob_Ls1_upper + 0.025 * len(Ls2)

    die = random.uniform(0.0, 1.0)
    if 0.0 <= die <= 0.1:
        return (POS_ROBOT.x, POS_ROBOT.y)
    elif 0.1 < die <= prob_Ls1_upper:
        return random.choice(Ls1)
    elif prob_Ls1_upper < die <= prob_Ls2_upper:
        return random.choice(Ls2)
    else:
        return (None, None)


def main():

    count = Counter()
    for _ in range(int(1e4)):
        count[read_sensor()] += 1
    print(count)


if __name__ == "__main__":
    main()
