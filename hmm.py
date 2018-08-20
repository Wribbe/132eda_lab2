#!/bin/env python3

import random
from collections import Counter

NUM_ROWS = 8
NUM_COLS = 8

N, W, S, E = HEADINGS = [0, 1, 2, 3]
HEADING_TO_CHAR = {
    N: 'N',
    W: 'W',
    S: 'S',
    E: 'E',
}

NUM_HEADINGS = len(HEADINGS)

NUM_STATES = NUM_ROWS * NUM_COLS * NUM_HEADINGS
LEN_T = NUM_STATES * NUM_STATES

PROB_KEEPING_HEADING = 0.7

ROBOT_START_X = 0
ROBOT_START_Y = 0

ROBOT_START_HEADING = N

SENSOR_NOTHING = (None, None)

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
        return next_pos(self.x, self.y, self.heading)

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
                new_heading = random.choice(HEADINGS)
            return new_heading

        if self.facing_wall():
            self.heading = pick_new_heading()
        else:
            if die_roll() > PROB_KEEPING_HEADING:
                self.heading = pick_new_heading()

    def move(self):
        if self.facing_wall():
            self.new_heading()
        self.x, self.y = self.next_pos()

def out_of_bounds(x, y):
    return any([x < 0, y < 0, x >= NUM_COLS, y >= NUM_ROWS])

def die_roll():
    return random.uniform(0.0, 1.0)

def next_pos(x,y,heading):
    return {
        N: (x, y-1),
        E: (x+1, y),
        S: (x, y+1),
        W: (x-1, y),
    }[heading]

def possible_pos(x, y, heading):
    same = None
    other = []
    for h in HEADINGS:
        pos = next_pos(x,y,h)
        if out_of_bounds(*pos):
            continue
        elif h == heading:
            same = pos
        else:
            other.append((*pos, h))
    return (same, other)

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

def index(x,y,h):
    nh = NUM_HEADINGS
    return y*NUM_COLS*nh + x*nh + h

class MatT():
    def __init__(self):

        self.T = [[0.0]*NUM_STATES for _ in range(NUM_STATES)]
        self.set_values()

    def getT(self, x, y, heading):
        return self.T[index(x, y, heading)]

    def __getitem__(self, i):
        return self.T[i]

    def set_values(self):
        for y in range(NUM_ROWS):
            for x in range(NUM_COLS):
                for h in range(NUM_HEADINGS):
                    current_row = self.T[index(x,y,h)]
                    same, others = possible_pos(x, y, h)
                    total_probability = 1.0
                    if same:
                        current_row[index(*same, h)]=PROB_KEEPING_HEADING
                        total_probability -= PROB_KEEPING_HEADING
                    for oth in others:
                        prob_oth = total_probability/len(others)
                        current_row[index(*oth)] = prob_oth

class MatO():
    def __init__(self):

        self.prob_correct = 0.1
        self.prob_one_out = 0.05
        self.prob_two_out = 0.025

        self.O = [[0.0]*NUM_STATES for _ in range(NUM_STATES+1)]
        self.set_values()

    def probability(self, x, y, other_x, other_y):
        return self.O[index(x,y,N)][index(other_x,other_y,N)]

    def set_values(self):

        def min_max_ranges(x,y):
            NC = NUM_COLS
            NR = NUM_ROWS
            return (max(0, x-2),min(NC-1, x+2),max(0, y-2),min(NR-1, y+2))

        nothing_diag = self.O[-1]

        for y in range(NUM_ROWS):
            for x in range(NUM_COLS):

                n_Ls = 0
                n_Ls2 = 0

                diagonals = [self.O[index(x,y,h)] for h in HEADINGS]
                ix_min, ix_max, iy_min, iy_max = min_max_ranges(x,y)
                for iy in range(iy_min, iy_max+1):
                    for ix in range(ix_min, ix_max+1):
                        dx, dy = [abs(x-ix),abs(y-iy)]
                        if dx == 0 and dy == 0:
                            prob = self.prob_correct
                        elif 2 in [dx, dy]:
                            prob = self.prob_two_out
                            n_Ls2 += 1
                        else:
                            prob = self.prob_one_out
                            n_Ls += 1

                        for diag in diagonals:
                            for h in HEADINGS:
                                diag[index(ix,iy,h)] = prob

                prob_nothing = 1.0 - self.prob_correct - n_Ls * \
                    self.prob_one_out - n_Ls2*self.prob_two_out
                for h in HEADINGS:
                        nothing_diag[index(x,y,h)] = prob_nothing

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

def predict(t, T):
    return [sum([ft*fT for (ft,fT) in zip(t,T[i])]) for i in range(NUM_STATES)]

def update(t, O, reading):
    if reading == SENSOR_NOTHING:
        x, y = (NUM_COLS-1, NUM_ROWS)
        obs_diag = O.O[-1]
    else:
        obs_diag = O.O[index(*reading,N)]
    return [t*O for (t,O) in zip(t,obs_diag)]

def main():

    robot = Robot(ROBOT_START_X, ROBOT_START_Y, ROBOT_START_HEADING)

    #check_probabilites(robot)
    #check_probabilities_heading(robot)

    T = MatT()
    O = MatO()

    t = [1.0/NUM_STATES] * NUM_STATES

    print(t)
    t = predict(t,T)
    print("")
    print(t)
    print("")
    reading = robot.read_sensor()
    t = update(t,O,reading)
    print(t)
    print("")
    robot.move()

    #print(T.probability(0,0,E,1,0,E))
    #print(T.probability(0,0,N,0,1,S))
    #print(T.probability(2,2,N,3,2,E))

    return 0

if __name__ == "__main__":
    main()
