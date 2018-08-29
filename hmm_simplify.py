#!/usr/bin/env python3

NUM_COLS = 8
NUM_ROWS = 8

N,E,S,W = HEADINGS = range(4)
NUM_HEADINGS = len(HEADINGS)

NUM_STATES = NUM_COLS * NUM_ROWS * NUM_HEADINGS

T, O = [[[0]*NUM_STATES for _ in range(NUM_STATES)] for _ in range(2)]

def index_to_coords(i):
    y_diff, x_diff = [NUM_COLS*NUM_HEADINGS, NUM_HEADINGS]
    y = int(i/y_diff)
    x = int((i-y*y_diff) / x_diff)
    return (x,y,i%NUM_HEADINGS)

def coords_to_index(x,y,h):
    return y*NUM_COLS*NUM_HEADINGS + x*NUM_HEADINGS + h

def main():

    print(coords_to_index(7,7,N))
    print(index_to_coords(252))

    ROBOT = (0,0,N)

    t = [0]*NUM_STATES

if __name__ == "__main__":
    main()
