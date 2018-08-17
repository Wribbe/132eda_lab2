#!/bin/env python3

import random
from collections import Counter

NUM_ROWS = 8
NUM_COLS = 8

N, W, S, E = DIRECTIONS = [0, 1, 2, 3]
HEADING_TO_CHAR = {
    N: 'N',
    W: 'W',
    S: 'S',
    E: 'E',
}

ROBOT_START_X = 0
ROBOT_START_Y = 0

ROBOT_START_HEADING = N

SENSOR_NOTHING = (None, None)

PROB_KEEP_HEADING = 0.7

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
            N: (self.x, self.y-1),
            E: (self.x+1, self.y),
            S: (self.x, self.y+1),
            W: (self.x-1, self.y),
        }
        return possible_steps[self.heading]

    def facing_wall(self):
        return out_of_bounds(*self.next_pos())

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
                self.is_true_location(x,y),
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

        die = die_roll()
        if 0.0 <= die <= 0.1:
            return self.location()
        elif 0.1 < die <= prob_Ls1_upper:
            return random.choice(Ls1)
        elif prob_Ls1_upper < die <= prob_Ls2_upper:
            return random.choice(Ls2)
        else:
            return SENSOR_NOTHING

    def location(self):
        return (self.x, self.y)

    def is_true_location(self, x, y):
        return (x, y) == self.location()

    def new_heading(self):

        def pick_new_heading():
            new_heading = self.heading
            while (new_heading == self.heading):
                new_heading = random.choice(DIRECTIONS)
            return new_heading

        if self.facing_wall():
            self.heading = pick_new_heading()
        else:
            if die_roll() > PROB_KEEP_HEADING:
                self.heading = pick_new_heading()

def out_of_bounds(x, y):
    return any([x < 0, y < 0, x >= NUM_COLS, y >= NUM_ROWS])

def die_roll():
    return random.uniform(0.0, 1.0)

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
        elif robot.is_true_location(*coord):
            count_rings["True Location"] += value
        else:
            count_rings["Nothing"] += value

    print("")
    print("Actual readings ({}):".format(total))
    for text, value in count_rings.items():
        print("{}: {} -> {}/{} ~ {:.2f}%".format(text, value, value, total,
                                             (value/total)*100))
    print("")

class MatT():
    def __init__(self):
        self.T = self.init_matrix()

    def probability(self, current_x, current_y, current_heading, next_x,
                    next_y, next_heading):
        cx = current_x
        cy = current_y
        ch = current_heading
        nx = next_x
        ny = next_y
        nh = next_heading
        return self.T[ch][cy][cx][nh][ny][nx]

    def init_matrix(self):

        def base_matrix(f):
            return [[[f]*NUM_COLS for _ in range(NUM_ROWS)] for _ in
                    DIRECTIONS]

        return base_matrix(base_matrix(1.0))

class MatO():
    def __init__(self):
        self.O = [[[0.0]*min(NUM_ROWS, NUM_COLS)] for _ in
                  range(NUM_ROWS*NUM_COLS+1)]

    def __str__(self):
        text = []
        for row in self.O:
            text.append(' '.join(["{}".format(f) for f in row]))
        return '\n'.join(text)

def check_probabilities_heading(robot):

    count = Counter()
    total = 1e4
    for _ in range(int(total)):
        old = robot.heading
        robot.new_heading()
        if old == robot.heading:
            count["Keep"] += 1
        else:
            count["New"] += 1
    fmt = "Robot keeps heading: {:.2f}% of the time."
    print(fmt.format((count["Keep"]/total)*100))
    print("")

def main():

    robot = Robot(ROBOT_START_X, ROBOT_START_Y, ROBOT_START_HEADING)
    dict_directions = {DIR : 0.0 for DIR in DIRECTIONS}


    check_probabilites(robot)
    check_probabilities_heading(robot)

    T = MatT()
    print(T)
    O = MatO()
    print(O)

    return 0

if __name__ == "__main__":
    main()
