from hmm_simplify import N,E,S,W, HEADINGS

C = 'C'

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


def grid(x,y,width,height):
    for col in range(width):
        for row in range(height):
            box(col, row)

def draw(t, O, T, robot, poll, NCS, NRS):

    grid(0,0, NCS, NRS)
    x, y, h = [0, 0, 0]

    for i,value in enumerate(t):

        if i%len(HEADINGS) == 0:
            write_in_box(x,y,h,"{:.3f}".format(value))
            box_status(x,y,value)
            write_in_box(*(robot[:2]), C, 'R')

        h += 1
        if h >= len(HEADINGS):
            h = 0
            x += 1
        if x >= NCS:
            x = 0
            y += 1

    display_canvas()
