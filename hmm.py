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

def read_sensor():

    def get_circle_dist_from_robot(tiles):
        xs = range(POS_ROBOT.x - tiles, POS_ROBOT.x + tiles + 1)
        ys = range(POS_ROBOT.y - tiles, POS_ROBOT.y + tiles + 1)
        tiles = []
        for y in ys:
            for x in xs:
                print(x,y)
                if (x < 0 or y < 0) or (POS_ROBOT.x == x and POS_ROBOT.y == y):
                    continue
                tiles.append((x,y))
        return tiles

    Ls1 = get_circle_dist_from_robot(1)
    Ls2 = get_circle_dist_from_robot(2)


def main():

    print(read_sensor())


if __name__ == "__main__":
    main()
