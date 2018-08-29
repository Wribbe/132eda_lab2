#!/usr/bin/env python3

NCS = NUM_COLS = 8
NRS = NUM_ROWS = 8

N,E,S,W = HEADINGS = range(4)
NH = NUM_HEADINGS = len(HEADINGS)

P_KEEP_HEADING, P_SENSOR_TRUE, P_L1, P_L2 = [0.7, 0.1, 0.05, 0.025]

NUM_STATES = NUM_COLS * NUM_ROWS * NUM_HEADINGS

T, O = [[[0]*NUM_STATES for _ in range(NUM_STATES)] for _ in range(2)]

PN = POS_NEXT = {
    N: ( 0, -1),
    E: ( 1,  0),
    S: ( 0,  1),
    W: (-1,  0),
}
pos_next = lambda x,y,h: (x+POS_NEXT[h][0], y+POS_NEXT[h][1], h)
pos_valid = lambda tx,ty,h=N: all([tx>=0, tx<NCS, ty>=0, ty<NRS])

def pos_all(x,y):
    return [(x+tx, y+ty, h) for (h,(tx, ty)) in PN.items()]

def pos_all_sane(x,y):
    return [p for p in pos_all(x,y) if pos_valid(*p)]

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

def main():

    # Setup T-matrix.
    for im, matrix in enumerate(T):
        head, others = head_and_others(*index_to_coords(im))
        prob = 1.0
        if head:
            prob -= P_KEEP_HEADING
            matrix[coords_to_index(*head)] = P_KEEP_HEADING
        prob /= len(others)
        for pos in others:
            matrix[coords_to_index(*pos)] = prob

    # Setup O-matrix.
    mat_nothing = []
    for im, matrix in enumerate(O):
        L1, L2 = get_circles(*index_to_coords(im))
        for pos in L1:
            matrix[coords_to_index(*pos)] = P_L1
        for pos in L2:
            matrix[coords_to_index(*pos)] = P_L2
        mat_nothing.append(1.0-P_SENSOR_TRUE-len(L1)*P_L1/NH-len(L2)*P_L2/NH)
    O.append(mat_nothing)

    t = [0.0]*NUM_STATES

    ROBOT = (0,0,N)

if __name__ == "__main__":
    main()
