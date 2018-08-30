canvas = []

def match_canvas_dim(x,y,l,d):

    x = x+l if d == 'h' else x
    y = y+l if d == 'v' else y

    if canvas:
        x = max(x, max([len(r) for r in canvas]))

    while len(canvas)-1 < y:
        canvas.append([])

    for y, row in enumerate(canvas):
        if x > len(row)-1:
            canvas[y] += [' ']*(x-len(row)-1)

def hline(x,y,l):
    match_canvas_dim(x,y,l,'h')
    canvas[y][x:x+l] = '_'*l

def vline(x,y,l):
    match_canvas_dim(x,y,l,'v')
    for y in range(y,y+l+1):
        canvas[y][x] = '|'

def draw(t, O, T, robot, poll):
    hline(11,10,20)
    vline(10,11,20)
    for line in canvas:
        print(''.join(line))
