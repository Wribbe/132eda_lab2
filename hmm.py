#!/bin/env python3

import random
from collections import Counter

NUM_ROWS = 8
NUM_COLS = 8

DIRECTIONS = ['N', 'W', 'S', 'E']
N, W, S, E = DIRECTIONS

ROBOT_START_X = 0
ROBOT_START_Y = 0

ROBOT_START_HEADING = N

class Robot:
    def __init__(self, x, y, heading):
        self.x = x
        self.y = y
        self.heading = heading

    def probabilites(self):
        return (self.prob_Ls1_upper-0.1,
                self.prob_Ls2_upper-self.prob_Ls1_upper,
                1.0-self.prob_Ls2_upper)

    def next_pos(self):
        possible_steps = {
            N: (self.x, self.y+1),
            E: (self.x+1, self.y),
            S: (self.x, self.y-1),
            W: (self.x-1, self.y),
        }
        return possible_steps[self.heading]

    def facing_wall(self):
        return out_of_bounds(self.next_pos())

    def get_circle_dist_from_robot(self, tiles):
        xs = range(self.x - tiles, self.x + tiles + 1)
        ys = range(self.y - tiles, self.y + tiles + 1)

        def not_max_or_min(x, y):
            x_not_max_or_min = x not in [min(xs), max(xs)]
            y_not_may_or_min = y not in [min(ys), max(ys)]
            return x_not_max_or_min and y_not_may_or_min

        def invalid_coords(x,y):
            return any([
                not_max_or_min(x,y),
                out_of_bounds(x,y),
                self.is_robot_locotion(x,y),
            ])

        tiles = []
        for y in ys:
            for x in xs:
                if not invalid_coords(x,y):
                    tiles.append((x,y))
        return tiles

    def read_sensor(self):

        Ls1 = self.get_circle_dist_from_robot(1)
        Ls2 = self.get_circle_dist_from_robot(2)

        self.Ls1 = Ls1
        self.Ls2 = Ls2

        prob_Ls1_upper = 0.1 + 0.05 * len(Ls1)
        prob_Ls2_upper = prob_Ls1_upper + 0.025 * len(Ls2)

        self.prob_Ls1_upper = prob_Ls1_upper
        self.prob_Ls2_upper = prob_Ls2_upper

        die = random.uniform(0.0, 1.0)
        if 0.0 <= die <= 0.1:
            return self.get_robot_location()
        elif 0.1 < die <= prob_Ls1_upper:
            return random.choice(Ls1)
        elif prob_Ls1_upper < die <= prob_Ls2_upper:
            return random.choice(Ls2)
        else:
            return (None, None)

    def get_robot_location(self):
        return (self.x, self.y)

    def is_robot_locotion(self, x, y):
        return (x, y) == self.get_robot_location()

def out_of_bounds(x, y):
    return (x < 0 or y < 0) or (x >= NUM_COLS or y >= NUM_ROWS)

def check_probabilites(robot):

    count = Counter()
    total = 1e4
    for _ in range(int(total)):
        count[robot.read_sensor()] += 1
    print("Current probabilities: ")
    fmt = "{}: {}%"
    print(fmt.format("correct", 10.0))
    for (text, value) in zip(["prob_L1", "prob_L2", "prob_nothing"],
                             [v*100 for v in robot.probabilites()]):
        print(fmt.format(text, value))

    count_rings = Counter()
    for coord, value in count.items():
        if coord in robot.Ls1:
            count_rings["Ls1"] += value
        elif coord in robot.Ls2:
            count_rings["Ls2"] += value
        elif coord == robot.get_robot_location():
            count_rings["True Location"] += value
        else:
            count_rings["Nothing"] += value

    print("")
    print("Actual readings ({}):".format(total))
    for text, value in count_rings.items():
        print("{}: {} -> {}/{} ~ {:.2f}%".format(text, value, value, total,
                                             (value/total)*100))

def main():

    ROBOT = Robot(ROBOT_START_X, ROBOT_START_Y, ROBOT_START_HEADING)
    DICT_DIRECTIONS = {DIR : 0.0 for DIR in DIRECTIONS}
    MATRIX = [[DICT_DIRECTIONS]*NUM_COLS for _ in range(NUM_ROWS)]

    check_probabilites(ROBOT)

    return 0

if __name__ == "__main__":
    main()
