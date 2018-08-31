import os

from hmm import \
    N,E,S,W, HEADINGS, SENSOR_NONE, coords_to_index, index_to_coords

C = 'C'
TR = 'TR'
BR = 'BR'
NH = len(HEADINGS)

MODES = ['tracking','headings','prob_nothing']
MODE_TITLES = ['Tracking','Headings','Probability nothing']
MODE_CURRENT = 0

INFO_DEFAULT = \
"""
    [t]: Next mode, [q]: quit
"""

MODE_INFO = [
    """
    [Enter/No input]: Move robot.
    Markers: SS - Sensor, R - Robot, ?? - Guess, H,M,L,0 = P[>0.3,>0.1,>0.000]
    """,
    """
    [Enter/No input]: Cycle through headings.
    """,
    """
    [Enter/No input]: Nothing.
    """,
]

canvas = []

box_width = 15
box_height = 7

heading_marker = 0

grid_offset_x = 0
grid_offset_y = 0

iterations = 0
sum_manhattan = 0

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
    return (x+grid_offset_x,y+grid_offset_y)

def clear_box(cx,cy):
    x,y = [v+1 for v in canvas_coords(cx,cy)]
    for yy in range(y,y+box_height-1):
        for xx in range(x,x+box_width):
            canvas[yy][xx] = ' '

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

def write_at(x,y,text):
    canvas[y] = [' ']*len(canvas[y])
    for i,c in enumerate(text):
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
            clear_box(x,y)

def mark_poll(poll):
    if poll != SENSOR_NONE:
        write_in_box(*poll[:2], TR, 'S')
        write_in_box(*poll[:2], C, ' SS')


def grid(x,y,width,height):
    global grid_offset_x, grid_offset_y
    grid_offset_x = x
    grid_offset_y = y
    for col in range(width):
        for row in range(height):
            box(col, row)

def mark_robot(robot):
    write_in_box(*(robot[:2]), C, 'R')

def mark_guess(x,y):
    write_in_box(x,y, BR, '?')
    write_in_box(x,y, C, '??')

def current_mode():
    return MODES[MODE_CURRENT]

def next_mode():
    global MODE_CURRENT
    MODE_CURRENT = (MODE_CURRENT+1)%len(MODES)
    return MODES[MODE_CURRENT]

def mark_marker():
    markers = {
        N: "A",
        E: ">",
        S: "V",
        W: "<",
    }
    x,y,h = index_to_coords(heading_marker)
    write_in_box(x,y,C,markers[h])

def mark_advance(mat):
    global heading_marker
    heading_marker = (heading_marker+1)%len(mat)

def draw(t, O, T, robot, poll, NCS, NRS, inp, guess, mode):

    os.system("cls" if os.name == "nt" else "clear")
    grid(0,1, NCS, NRS)
    write_at(0,0,"Mode: {}".format(MODE_TITLES[MODE_CURRENT]))
    clear_tiles(NCS, NRS)

    sum_headings = lambda mat,i: sum(mat[i:i+NH])

    if mode == 'tracking':
        mat = t
        indexes = range(0,len(mat),NH)
        disp_value = sum_headings
        if not inp: # Enter.
            global iterations
            iterations += 1
    else:
        if mode == 'headings':
            if not inp: # Enter.
                mark_advance(T)
            mat = T[heading_marker]
        else:
            mat = O[-1]
        indexes = range(len(mat))
        disp_value = lambda mat,i: mat[i]

    for i in indexes:
        x,y,h = index_to_coords(i)
        value = disp_value(mat,i)
        write_in_box(x,y,h,"{:.3f}".format(value))
        if mode == 'tracking':
            box_status(x,y,value)

    if mode == 'tracking':
        mark_poll(poll)
        mark_guess(*guess)
        mark_robot(robot)
    if mode == 'headings':
        mark_marker()
    display_canvas()
    info_mode = MODE_INFO[MODE_CURRENT].strip()
    print("{} {}".format(INFO_DEFAULT.strip('\n'),info_mode))

    if mode == 'tracking':
        fmt = "    Iteration: {}, Manhattan distance: {}, avg. Manhattan {}"
        manhattan = sum([abs(v1-v2) for v1,v2 in zip(guess,robot[:2])])
        global sum_manhattan
        sum_manhattan += manhattan
        avg = sum_manhattan/iterations
        print(fmt.format(iterations, manhattan, avg))

    return input("\nEnter option and press <ENTER>: ")
