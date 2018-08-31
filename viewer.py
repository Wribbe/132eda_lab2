import os

from hmm_simplify import N,E,S,W, HEADINGS, SENSOR_NONE
from hmm_simplify import coords_to_index, index_to_coords

C = 'C'
TR = 'TR'
BR = 'BR'
NH = len(HEADINGS)

canvas = []

box_width = 15
box_height = 7

def display_canvas():
    print('\n'.join([''.join(line) for line in canvas]))

def match_canvas_dim(x,y,l,d):

    x = x+l if d == 'h' else x
    y = y+l if d == 'v' else y

    if canvas:
        x = max(x, max([len(r)-1 for r in canvas]))

    while len(canvas)-1 < y:
        canvas.append([])

    for y, row in enumerate(canvas):
        canvas[y] += [' ']*(x-(len(row)-1))

def hline(x,y,l,char='_'):
    match_canvas_dim(x,y,l,'h')
    canvas[y][x:x+l] = char*l

def vline(x,y,l):
    match_canvas_dim(x,y,l,'v')
    for y in range(y,y+l):
        canvas[y][x] = '|'

def canvas_coords(cx,cy):
    x = box_width*cx
    x += 1*cx if cx else 0
    y = box_height*cy
    return (x,y)

def write_in_box(cx,cy,pos,text):
    x,y = [v+1 for v  in canvas_coords(cx,cy)]
    middle_x = int((box_width/2)-(len(text)/2))
    middle_y = int((box_height/2))
    offset = {
        N: (middle_x, 0),
        E: (box_width-len(text), middle_y),
        S: (middle_x, box_height-1),
        W: (0, middle_y),
        C: (middle_x, middle_y),
        TR: (box_width-1, 0),
        BR: (box_width-1, box_height-1),
    }
    x,y = [v1+v2 for (v1,v2) in zip([x,y],offset[pos])]
    for i, c in enumerate(text):
        canvas[y][x+i] = c

def box(cx,cy):

    x,y = canvas_coords(cx,cy)

    hline(x+1,y,box_width)
    hline(x+1,y+box_height,box_width)

    vline(x,y+1,box_height)
    vline(x+box_width+1,y+1,box_height)

def box_status(x,y,value):
    x,y = [v+1 for v  in canvas_coords(x,y)]
    status = '0'
    if value > 0.3:
        status = 'H'
    elif value > 0.1:
        status = 'M'
    elif round(value, 3) > 0.0:
        status = 'L'
    canvas[y][x] = status

def clear_tiles(xmax,ymax):
    for x in range(xmax):
        for y in range(ymax):
            write_in_box(x,y, C, ' '*(box_width-2))
            write_in_box(x,y, TR, ' ')

def mark_poll(poll):
    if poll != SENSOR_NONE:
        write_in_box(*poll[:2], TR, 'S')
        write_in_box(*poll[:2], C, ' SS')


def grid(x,y,width,height):
    for col in range(width):
        for row in range(height):
            box(col, row)

def mark_robot(robot):
    write_in_box(*(robot[:2]), C, 'R')

def mark_guess(x,y):
    write_in_box(x,y, BR, '?')
    write_in_box(x,y, C, '??')

def draw(t, O, T, robot, poll, NCS, NRS, inp, guess):

    os.system("cls" if os.name == "nt" else "clear")
    grid(0,0, NCS, NRS)
    x, y, h = [0, 0, 0]

    mat = t

    sum_headings = lambda mat,i: sum(mat[i:i+NH])

    indexes = range(0,len(mat),NH)

    for i in indexes:
        x,y,h = index_to_coords(i)
        heading_sum = sum_headings(mat, i)
        write_in_box(x,y,h,"{:.3f}".format(heading_sum))
        box_status(x,y,heading_sum)

    clear_tiles(NCS, NRS)
    mark_poll(poll)
    mark_guess(*guess)
    mark_robot(robot)
    display_canvas()
