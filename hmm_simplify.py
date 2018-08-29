#!/usr/bin/env python3

NCS = NUM_COLS = 8
NRS = NUM_ROWS = 8

N,E,S,W = HEADINGS = range(4)
NUM_HEADINGS = len(HEADINGS)

P_KEEP_HEADING, P_SENSOR_TRUE = [0.7, 0.1]

NUM_STATES = NUM_COLS * NUM_ROWS * NUM_HEADINGS

T, O = [[[0]*NUM_STATES for _ in range(NUM_STATES)] for _ in range(2)]

PN = POS_NEXT = {
    N: ( 0, -1),
    E: ( 1,  0),
    S: ( 0,  1),
    W: (-1,  0),
}
pos_next = lambda x,y,h: (x+POS_NEXT[h][0], y+POS_NEXT[h][1], h)

def pos_all(x,y):
    return [(x+tx, y+ty, h) for (h,(tx, ty)) in PN.items()]

def pos_all_sane(x,y):
    valid = lambda tx,ty,_: all([tx>=0, tx<NCS, ty>=0, ty<NRS])
    return [t for t in pos_all(x,y) if valid(*t)]

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

def coords_to_index(x,y,h):
    return y*NUM_COLS*NUM_HEADINGS + x*NUM_HEADINGS + h

def main():

    # Setup T-matrix.
    for im, matrix in enumerate(T):
        mx, my, mh = index_to_coords(im)
        head, others = head_and_others(mx,my,mh)
        print(head)
        prob = 1.0
        if head:
            prob -= P_KEEP_HEADING
            matrix[coords_to_index(*head)] = P_KEEP_HEADING
        prob /= len(others)
        for pos in others:
            matrix[coords_to_index(*pos)] = prob

    ROBOT = (0,0,N)

    t = [0]*NUM_STATES

if __name__ == "__main__":
    main()
