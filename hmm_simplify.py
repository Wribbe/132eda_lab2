#!/usr/bin/env python3

import random
import viewer

from random import choice as randch

NCS = NUM_COLS = 8
NRS = NUM_ROWS = 8

N,E,S,W = HEADINGS = range(4)
NH = NUM_HEADINGS = len(HEADINGS)
NUM_STATES = NUM_COLS * NUM_ROWS * NUM_HEADINGS

P_KEEP_HEADING, P_SENSOR_TRUE, P_L1, P_L2 = [0.7, 0.1, 0.05, 0.025]
SENSOR_NONE = (None, None)

T, TT, O = [[[0]*NUM_STATES for _ in range(NUM_STATES)] for _ in range(3)]

PN = POS_NEXT = {
    N: ( 0, -1),
    E: ( 1,  0),
    S: ( 0,  1),
    W: (-1,  0),
}

# Position / coordinates / index - helper methods.
pos_next = lambda x,y,h: (x+POS_NEXT[h][0], y+POS_NEXT[h][1], h)
pos_valid = lambda tx,ty,h=N: all([tx>=0, tx<NCS, ty>=0, ty<NRS])
pos_all = lambda x,y: [(x+tx, y+ty, h) for (h,(tx, ty)) in PN.items()]
pos_all_sane = lambda x,y: [p for p in pos_all(x,y) if pos_valid(*p)]
coords_to_index = lambda x,y,h: y*NUM_COLS*NUM_HEADINGS + x*NUM_HEADINGS + h
tcoords_to_index = lambda x,y,h: coords_to_index(y,x,h) # Transposition.

# Robot related helper methods.
roll = lambda: random.uniform(0.0, 1.0)
rh = lambda h: randch([v for v in HEADINGS if v != h])
roll_heading = lambda x,y,h: (x,y,rh(h)) if roll()<=P_KEEP_HEADING else (x,y,h)

# Probability helper methods
p_tot_L1 = lambda l: len(l)/NH * P_L1
p_tot_L2 = lambda l: len(l)/NH * P_L2

def head_and_others(x,y,h):
    sane = pos_all_sane(x,y)
    head = [(i,p) for i,p in enumerate(sane) if p == pos_next(x,y,h)]
    if head:
        del sane[head[0][0]]
        return (head[0][1], sane)
    return (None, sane)

def index_to_coords(i):
    y_diff, x_diff = [NUM_COLS*NUM_HEADINGS, NUM_HEADINGS]
    y = int(i/y_diff)
    x = int((i-y*y_diff) / x_diff)
    return (x,y,i%NUM_HEADINGS)

def get_circles(x,y,h=None):
    L1 = []; L2 = []
    for xx in range(x-2, x+3):
        for yy in range(y-2, y+3):
            diffs = [abs(xx-x), abs(yy-y)]
            if pos_valid(xx,yy) and any(diffs):
                if all([d <= 1 for d in diffs]):
                    L1 += [(xx,yy,h) for h in HEADINGS]
                else:
                    L2 += [(xx,yy,h) for h in HEADINGS]
    return (L1, L2)

def move(robot):
    next_p = pos_next(*robot)
    while not pos_valid(*next_p):
        robot = roll_heading(*robot)
        next_p = pos_next(*robot)
    return next_p

def poll_sensor(robot):
    L1, L2 = get_circles(*robot)
    probs = [
        (P_SENSOR_TRUE, robot),
        (p_tot_L1(L1), random.choice(L1)),
        (p_tot_L2(L2), random.choice(L2)),
    ]
    r = roll()
    for i, (prob, ret) in enumerate(probs):
        if r <= sum([p for (p,_) in probs[0:i]]):
            return ret
    return SENSOR_NONE

def forward(t, O, T, robot):
    t = [sum([v1*v2 for v1,v2 in zip(t,vT)]) for vT in T] # Prediction.
    poll = poll_sensor(robot)
    o = O[-1] if poll == SENSOR_NONE else O[coords_to_index(*poll)]
    t = [vt*vo for vt,vo in zip (t,o)] # Update.
    return ([v/sum(t) for v in t], poll) # Normalize.

def main():

    # Setup T-/TT-matrix.
    for im, (mT, mTT) in enumerate(zip(T,TT)):
        head, others = head_and_others(*index_to_coords(im))
        prob = 1.0
        if head:
            prob -= P_KEEP_HEADING
            mT[coords_to_index(*head)] = mTT[tcoords_to_index(*head)] = 1-prob
        prob /= len(others)
        for pos in others:
            mT[coords_to_index(*pos)] = mTT[tcoords_to_index(*pos)] = prob

    # Setup O-matrix.
    O.append([])
    for im, matrix in enumerate(O):
        L1, L2 = get_circles(*index_to_coords(im))
        for pos in L1:
            matrix[coords_to_index(*pos)] = P_L1
        for pos in L2:
            matrix[coords_to_index(*pos)] = P_L2
        O[-1].append(1.0-P_SENSOR_TRUE-p_tot_L1(L1)-p_tot_L2(L2))

    t = [1.0/NUM_STATES]*NUM_STATES

    # Init robot and main loop.
    robot = (randch(range(NCS)), randch(range(NRS)), rh(-1))
    inp = None
    while inp != 'q':
        t, poll = forward(t, O, TT, robot)
        robot = move(robot)
        viewer.draw(t, O, TT, robot, poll)
        inp = input("Enter option and press <ENTER>: ")

if __name__ == "__main__":
    main()
