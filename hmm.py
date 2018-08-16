#!/bin/env python3

NUM_ROWS = 8
NUM_COLS = 8

DIRECTIONS = ['N', 'W', 'S', 'E']
N, W, S, E = DIRECTIONS

DICT_DIRECTIONS = {DIR : 0.0 for DIR in DIRECTIONS}

def main():

    matrix = [[DICT_DIRECTIONS]*NUM_COLS for _ in range(NUM_ROWS)]
    print(matrix)

if __name__ == "__main__":
    main()
