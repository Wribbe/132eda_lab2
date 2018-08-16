#!/bin/env python3

import random

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
    print(Ls1)
    Ls2 = get_circle_dist_from_robot(2)
    print(Ls2)


def main():

    print(read_sensor())


if __name__ == "__main__":
    main()
