canvas = []

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

def box(cx,cy):

    width = 10
    height = 5

    x = width*cx
    x += 1 if cx else 0

    y = height*cy

    hline(x+1,y,width)
    hline(x+1,y+height,width)

    vline(x,y+1,height)
    vline(x+width+1,y+1,height)

def draw(t, O, T, robot, poll):
    box(0,0)
    box(0,1)
    box(1,1)
    box(1,0)
    display_canvas()
