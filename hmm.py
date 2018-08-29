#!/usr/bin/env python3

import random
from collections import Counter

NUM_ROWS = 10
NUM_COLS = 10

N, E, S, W = HEADINGS = [0, 1, 2, 3]
HEADING_TO_CHAR = {
    N: 'N',
    W: 'W',
    S: 'S',
    E: 'E',
}

NUM_HEADINGS = len(HEADINGS)

NUM_STATES = NUM_ROWS * NUM_COLS * NUM_HEADINGS
LEN_T = NUM_STATES * NUM_STATES

PROB_KEEPING_HEADING = 0.7

ROBOT_START_X = 0
ROBOT_START_Y = 0

ROBOT_START_HEADING = N

SENSOR_NOTHING = (None, None)

class Robot:
    def __init__(self, x, y, heading):
        self.x = x
        self.y = y
        self.heading = heading

    def probabilites(self):
        return (self.prob_Ls1_upper-0.1,
                self.prob_Ls2_upper-self.prob_Ls1_upper,
                1.0-self.prob_Ls2_upper)

    def next_pos(self):
        return next_pos(self.x, self.y, self.heading)

    def facing_wall(self):
        return out_of_bounds(*self.next_pos())

    def get_circle_dist_from_robot(self, tiles):
        xs = range(self.x - tiles, self.x + tiles + 1)
        ys = range(self.y - tiles, self.y + tiles + 1)

        def not_max_or_min(x, y):
            x_not_max_or_min = x not in [min(xs), max(xs)]
            y_not_may_or_min = y not in [min(ys), max(ys)]
            return x_not_max_or_min and y_not_may_or_min

        def invalid_coords(x,y):
            return any([
                not_max_or_min(x,y),
                out_of_bounds(x,y),
                self.is_true_location(x,y),
            ])

        tiles = []
        for y in ys:
            for x in xs:
                if not invalid_coords(x,y):
                    tiles.append((x,y))
        return tiles

    def read_sensor(self):

        Ls1 = self.get_circle_dist_from_robot(1)
        Ls2 = self.get_circle_dist_from_robot(2)

        self.Ls1 = Ls1
        self.Ls2 = Ls2

        prob_Ls1_upper = 0.1 + 0.05 * len(Ls1)
        prob_Ls2_upper = prob_Ls1_upper + 0.025 * len(Ls2)

        self.prob_Ls1_upper = prob_Ls1_upper
        self.prob_Ls2_upper = prob_Ls2_upper

        die = die_roll()
        if 0.0 <= die <= 0.1:
            return self.location()
        elif 0.1 < die <= prob_Ls1_upper:
            return random.choice(Ls1)
        elif prob_Ls1_upper < die <= prob_Ls2_upper:
            return random.choice(Ls2)
        else:
            return SENSOR_NOTHING

    def location(self):
        return (self.x, self.y)

    def is_true_location(self, x, y):
        return (x, y) == self.location()

    def new_heading(self):

        def pick_new_heading():
            new_heading = self.heading
            while (new_heading == self.heading):
                new_heading = random.choice(HEADINGS)
            return new_heading

        if self.facing_wall():
            self.heading = pick_new_heading()
        else:
            if die_roll() > PROB_KEEPING_HEADING:
                self.heading = pick_new_heading()

    def move(self):
        self.new_heading()
        while self.facing_wall():
            self.new_heading()
        self.x, self.y = self.next_pos()

def out_of_bounds(x, y):
    return any([x < 0, y < 0, x >= NUM_COLS, y >= NUM_ROWS])

def die_roll():
    return random.uniform(0.0, 1.0)

def next_pos(x,y,heading):
    return {
        N: (x, y-1),
        E: (x+1, y),
        S: (x, y+1),
        W: (x-1, y),
    }[heading]

def possible_pos(x, y, heading):
    same = None
    other = []
    for h in HEADINGS:
        pos = next_pos(x,y,h)
        if out_of_bounds(*pos):
            continue
        elif h == heading:
            same = pos
        else:
            other.append((*pos, h))
    return (same, other)

def check_probabilites(robot):

    count = Counter()
    total = 1e4
    for _ in range(int(total)):
        count[robot.read_sensor()] += 1
    print("Current probabilities: ")
    fmt = "{}: {}%"
    print(fmt.format("correct", 10.0))
    for (text, value) in zip(["prob_L1", "prob_L2", "prob_nothing"],
                             [v*100 for v in robot.probabilites()]):
        print(fmt.format(text, value))

    count_rings = Counter()
    for coord, value in count.items():
        if coord in robot.Ls1:
            count_rings["Ls1"] += value
        elif coord in robot.Ls2:
            count_rings["Ls2"] += value
        elif robot.is_true_location(*coord):
            count_rings["True Location"] += value
        else:
            count_rings["Nothing"] += value

    print("")
    print("Actual readings ({}):".format(total))
    for text, value in count_rings.items():
        print("{}: {} -> {}/{} ~ {:.2f}%".format(text, value, value, total,
                                             (value/total)*100))
    print("")

def index(x,y,h):
    nh = NUM_HEADINGS
    return y*NUM_COLS*nh + x*nh + h

def coords(index):
    nh = NUM_HEADINGS
    y = int(index/NUM_COLS/nh)
    x = int((index - y*NUM_COLS*nh)/nh)
    return (x,y,N)

class MatT():
    def __init__(self):
        self.T = self.initT()
        self.set_values()

    def initT(self):
        return [[0.0]*NUM_STATES for _ in range(NUM_STATES)]

    def getT(self, x, y, heading):
        return self.T[index(x, y, heading)]

    def __getitem__(self, i):
        return self.T[i]

    def set_values(self):
        for y in range(NUM_ROWS):
            for x in range(NUM_COLS):
                for h in range(NUM_HEADINGS):
                    current_row = self.T[index(x,y,h)]
                    same, others = possible_pos(x, y, h)
                    total_probability = 1.0
                    if same:
                        current_row[index(*same, h)]=PROB_KEEPING_HEADING
                        total_probability -= PROB_KEEPING_HEADING
                    for oth in others:
                        prob_oth = total_probability/len(others)
                        current_row[index(*oth)] = prob_oth

    def transpose(self):
        tempT = self.initT()
        for y in range(NUM_STATES):
            for x in range(NUM_STATES):
                tempT[y][x] = self.T[x][y]
        self.T = tempT

class MatO():
    def __init__(self):

        self.prob_correct = 0.1
        self.prob_one_out = 0.05
        self.prob_two_out = 0.025

        self.O = [[0.0]*NUM_STATES for _ in range(NUM_STATES+1)]
        self.set_values()

    def probability(self, x, y, other_x, other_y):
        return self.O[index(x,y,N)][index(other_x,other_y,N)]

    def set_values(self):

        def min_max_ranges(x,y):
            NC = NUM_COLS
            NR = NUM_ROWS
            return (max(0, x-2),min(NC-1, x+2),max(0, y-2),min(NR-1, y+2))

        nothing_diag = self.O[-1]

        for y in range(NUM_ROWS):
            for x in range(NUM_COLS):

                n_Ls = 0
                n_Ls2 = 0

                diagonals = [self.O[index(x,y,h)] for h in HEADINGS]
                ix_min, ix_max, iy_min, iy_max = min_max_ranges(x,y)
                for iy in range(iy_min, iy_max+1):
                    for ix in range(ix_min, ix_max+1):
                        dx, dy = [abs(x-ix),abs(y-iy)]
                        if dx == 0 and dy == 0:
                            prob = self.prob_correct
                        elif 2 in [dx, dy]:
                            prob = self.prob_two_out
                            n_Ls2 += 1
                        else:
                            prob = self.prob_one_out
                            n_Ls += 1

                        for diag in diagonals:
                            for h in HEADINGS:
                                diag[index(ix,iy,h)] = prob

                prob_nothing = 1.0 - self.prob_correct - n_Ls * \
                    self.prob_one_out - n_Ls2*self.prob_two_out
                for h in HEADINGS:
                        nothing_diag[index(x,y,h)] = prob_nothing

    def __getitem__(self, i):
        return self.O[i]

def check_probabilities_heading(robot):

    count = Counter()
    total = 1e4
    for _ in range(int(total)):
        old = robot.heading
        robot.new_heading()
        if old == robot.heading:
            count["Keep"] += 1
        else:
            count["New"] += 1
    fmt = "Robot keeps heading: {:.2f}% of the time."
    print(fmt.format((count["Keep"]/total)*100))
    print("")

def normalize(l):
    sum_l = sum(l)
    return [v/sum_l for v in l]

def predict(t, T):
    return [sum([ft*fT for (ft,fT) in zip(t,T[i])]) for i in
                      range(NUM_STATES)]

def update(t, O, reading):
    if reading == SENSOR_NOTHING:
        x, y = (NUM_COLS-1, NUM_ROWS)
        obs_diag = O.O[-1]
    else:
        obs_diag = O.O[index(*reading,N)]
    return [t*O for (t,O) in zip(t,obs_diag)]

def main(stdscr=None):

    robot = Robot(ROBOT_START_X, ROBOT_START_Y, ROBOT_START_HEADING)

    #check_probabilites(robot)
    #check_probabilities_heading(robot)

    T = MatT()
    TT = MatT()
    TT.transpose()
    O = MatO()

    t = [1.0/NUM_STATES] * NUM_STATES

    print(t)
    t = predict(t,T)
    print("")
    print(t)
    print("")
    reading = robot.read_sensor()
    t = update(t,O,reading)
    print(t)
    print("")
    robot.move()

    if (stdscr):
        draw(stdscr, robot, T, TT, O, t)

def draw(stdscr, robot, T, TT, O, t):

    def between(start, stop, increment=1):
        return range(start, start+stop, increment)

    def draw_grid():
        for x in between(grid_start_x, (NUM_COLS+1)*tile_width, tile_width):
            stdscr.vline(grid_start_y, x, curses.ACS_VLINE, grid_num_char_y)
            for y in between(grid_start_y, grid_end_y, tile_height):
                if x == grid_start_x:
                    stdscr.hline(y,x,curses.ACS_HLINE,grid_num_char_x)
                if y == grid_start_y and x == grid_start_x:
                    char = curses.ACS_ULCORNER
                elif y == grid_start_y and x == grid_end_x:
                    char = curses.ACS_URCORNER
                elif y == grid_end_y and x == grid_end_x:
                    char = curses.ACS_LRCORNER
                elif y == grid_end_y and x == grid_start_x:
                    char = curses.ACS_LLCORNER
                elif y == grid_start_y:
                    char = curses.ACS_TTEE
                elif y == grid_end_y:
                    char = curses.ACS_BTEE
                elif x == grid_end_x:
                    char = curses.ACS_RTEE
                elif x == grid_start_x:
                    char = curses.ACS_LTEE
                else:
                    char = curses.ACS_PLUS
                stdscr.vline(y, x, char, 1)
        for y in range(NUM_ROWS):
            for x in range(NUM_COLS):
                tilefill(x,y,colors["BG_DEFAULT"])

    def tilestr(x,y,heading,string):
        string = string.replace('0.', '.')
        x_center = int(((tile_width)/2)-(len(string)/2))
        y_center = int((tile_height)/2)
        offsets = {
            N: (x_center, 1),
            E: (tile_width-len(string), y_center),
            S: (x_center, tile_height-1),
            W: (1, y_center),
        }
        x_offset, y_offset = offsets[heading]
        rx = grid_start_x + x*tile_width + x_offset
        ry = grid_start_y + y*tile_height + y_offset
        stdscr.addstr(ry, rx, string, color_tiles[x][y][heading])

    def tilefill(x,y,color):
        rx = grid_start_x + x*tile_width + 1
        ry = grid_start_y + y*tile_height + 1
        for h in HEADINGS:
            color_tiles[x][y][h] = color
        for x in between(rx, tile_width-1):
            for y in between(ry, tile_height-1):
                stdscr.addstr(y,x,' ',color)

    def tilecenter(x,y,color):
        x_center = int((tile_width)/2)
        y_center = int((tile_height)/2)
        rx = grid_start_x + x*tile_width + x_center
        ry = grid_start_y + y*tile_height + y_center
        for y in range(ry, ry+2):
            for x in range(rx-1, rx+2):
                stdscr.addstr(y, x, ' ', color)

    def tilecorner(x,y,color):
        rx = grid_start_x + x*tile_width + 1
        ry = grid_start_y + (y+1)*tile_height - 1
        stdscr.addstr(ry, rx, ' ', color)
        stdscr.addstr(ry, rx+1, ' ', color)


    def infobar():
        current_x = pos_statusbar_x
        stdscr.addstr(pos_statusbar_y, pos_statusbar_x, ' '*128)
        for key, desc in sorted(keys["general"].items()):
            out = "{}: {}, ".format(key_to_string.get(key, key), desc)
            stdscr.addstr(pos_statusbar_y, current_x, out)
            current_x += len(out)
        mode = mode_list[current_mode]
        for key, desc in sorted(keys['modes'][mode].items()):
            out = "{}: {}, ".format(key_to_string.get(key, key), desc)
            stdscr.addstr(pos_statusbar_y, current_x, out)
            current_x += len(out)
        stdscr.addstr(pos_statusbar_y, current_x-2, ' ')

    def display_mode():
        stdscr.addstr(1, 0, " "*128, colors['BG_DEFAULT'])
        mode = mode_list[current_mode]
        stdscr.addstr(1, 1, "Mode: {}.".format(mode.capitalize()),
                      curses.A_STANDOUT)

    current_sensor = SENSOR_NOTHING

    current_cycle = (0,0,N)
    def fill_grid():

        sum_prob = False

        mat = None
        mode = mode_list[current_mode]

        if mode == 'probability nothing':
            mat = O[-1]
        elif mode == 'tracking':
            tilecenter(*robot.location(), colors["COLOR_TRUE"])
            if current_sensor != SENSOR_NOTHING:
                tilecorner(*current_sensor, colors["COLOR_SENSOR"])
            mat = t
            sum_prob = True
        elif mode == 'probability headings':
            mat = T[index(*current_cycle)]
            x,y,h = current_cycle
            color_tiles[x][y][h] = colors["BG_CYAN"]

        if mat:
            for y in range(NUM_ROWS):
                for x in range(NUM_COLS):
                    for h in HEADINGS:
                        if not sum_prob:
                            tilestr(x, y, h, "{:.3f}".format(mat[index(x,y,h)]))
                        else:
                            tilestr(x, y, N, "{:.3f}".format(prob_sum(x,y)))
                            break

    current_mode = 0

    def next_mode():
        nonlocal current_mode
        if current_mode+1 > len(keys['modes'])-1:
            current_mode = 0
        else:
            current_mode += 1
        return mode_list[current_mode]

    def cycle_headings():
        nonlocal current_cycle
        x,y,h = current_cycle
        if h == HEADINGS[-1]:
            h = HEADINGS[0]
            x += 1
        else:
            h += 1
        if x >= NUM_COLS:
            x = 0
            y += 1
        if y >= NUM_ROWS:
            y = 0
        current_cycle = (x,y,h)

    def manhattan_get():
        manhattan_x, manhattan_y = [0, 0]
        max_x, max_y = current_max
        current_x, current_y = robot.location()
        delta_x, delta_y = [1,1]
        if current_x < max_x:
            delta_x *= -1
        if current_y < max_y:
            delta_y *= -1
        while max_x != current_x:
            max_x += delta_x
            manhattan_x += 1
        while max_y != current_y:
            max_y += delta_y
            manhattan_y += 1
        return manhattan_x + manhattan_y

    def prob_sum(x,y):
        i = index(x,y,N)
        return sum(t[i:i+NUM_HEADINGS])

    def info_trancking():
        nonlocal sum_manhattan
        y = pos_info_tracking_y
        x = tile_border
        stdscr.addstr(y, x, "Iteration: {}".format(iterations_tracking))
        dist_manhattan = manhattan_get()
        sum_manhattan += dist_manhattan
        y+= 1
        stdscr.addstr(y, x, " "*128)
        stdscr.addstr(y, x, "Manhattan dist: {}".format(dist_manhattan))
        y+= 1
        if (sum_manhattan and iterations_tracking):
            manhattan_avg = sum_manhattan / iterations_tracking
            stdscr.addstr(y, x, "Avg. manhattan: {}".format(manhattan_avg))
        else:
            stdscr.addstr(y, x, "Avg. manhattan: {}".format("..."))

    def calc_relations():
        center = [int(v) for v in [curses.LINES/2, curses.COLS/2]]
        ratio = int(curses.COLS / curses.LINES)
        tile_height = 0
        tile_width = 0
        if (curses.COLS < curses.LINES):
            tile_side = int((curses.COLS-2*tile_border)/NUM_COLS)
            tile_height = tile_side*2
            tile_width = tile_side
        else:
            tile_side = int((curses.LINES-2*tile_border)/NUM_ROWS)
            tile_height = tile_side
            tile_width = tile_side*2


        grid_start_x = int(center[1]-(NUM_COLS/2)*tile_width)
        grid_end_x = grid_start_x+tile_width*NUM_COLS
        grid_num_char_x = grid_end_x - grid_start_x
        x_stop = int(center[1]+(NUM_COLS/2)*tile_width)

        grid_end_y = grid_start_y+tile_height*NUM_ROWS
        grid_num_char_y = grid_end_y - grid_start_y

        pos_statusbar_y = grid_start_y + tile_height*NUM_ROWS + \
            pos_statusbar_offset_y
        pos_statusbar_x = tile_border

        pos_info_tracking_y = pos_statusbar_y + 2

        return [center, ratio, tile_height, tile_width, grid_start_x,
                grid_end_x, grid_num_char_x, x_stop, grid_end_y,
                grid_num_char_y, pos_statusbar_y, pos_statusbar_x,
                pos_info_tracking_y]


    curses.start_color()

   # Clear screen
    stdscr.clear()

    curses.curs_set(0)

    tile_border = 6
    grid_start_y = 5
    pos_statusbar_offset_y = 2

    center, ratio, tile_height, tile_width, grid_start_x, grid_end_x, \
    grid_num_char_x, x_stop, grid_end_y, grid_num_char_y, pos_statusbar_y, \
    pos_statusbar_x, pos_info_tracking_y = calc_relations()

    current_cols = curses.COLS
    current_lines = curses.LINES

    colors = {
        "BG_DEFAULT": (curses.COLOR_BLACK, curses.COLOR_WHITE),
        "BG_RED": (curses.COLOR_BLACK, curses.COLOR_RED),
        "BG_GREEN": (curses.COLOR_BLACK, curses.COLOR_GREEN),
        "BG_YELLOW": (curses.COLOR_BLACK, curses.COLOR_YELLOW),
        "BG_MAGENTA": (curses.COLOR_BLACK, curses.COLOR_MAGENTA),
        "BG_BLUE": (curses.COLOR_BLACK, curses.COLOR_BLUE),
        "COLOR_TRUE": (curses.COLOR_BLACK, curses.COLOR_BLACK),
        "COLOR_SENSOR": (curses.COLOR_CYAN, curses.COLOR_CYAN),
        "BG_CYAN": (curses.COLOR_BLACK, curses.COLOR_CYAN),
        "COLOR_MAX": (curses.COLOR_BLUE, curses.COLOR_BLUE),
    }

    for i, (name, pair) in enumerate(colors.items(), start=1):
        curses.init_pair(i, *pair)
        colors[name] = curses.color_pair(i)

    color_tiles = [[[colors["BG_DEFAULT"] for _ in range(NUM_HEADINGS)] for _
                    in  range(NUM_COLS)] for _ in range(NUM_ROWS)]
    stdscr.bkgd(' ', colors["BG_DEFAULT"])

    KEY_QUIT = 'q'
    KEY_SWITCH_MODE = '\t'
    KEY_NEXT = 'n'

    key_to_string = {
        '\t': "TAB",
    }

    keys = {
        'general': {
            KEY_QUIT: "Quit",
            KEY_SWITCH_MODE: "Switch mode",
        },
        'modes': {
            'tracking': {
                KEY_NEXT: "Step robot",
            },
            'probability headings': {
                KEY_NEXT: "Cycle headings",
            },
            'probability nothing': {
            },
        },
    }

    mode_list = list(keys['modes'].keys())
    current_max = (0,0)

    iterations_tracking = 0
    sum_manhattan = 0

    key = None
    while key != KEY_QUIT:

        resized = curses.is_term_resized(curses.LINES, curses.COLS)
        if resized:
            stdscr.clear()
            curses.LINES, curses.COLS = stdscr.getmaxyx()
            center, ratio, tile_height, tile_width, grid_start_x, grid_end_x, \
            grid_num_char_x, x_stop, grid_end_y, grid_num_char_y, pos_statusbar_y, \
            pos_statusbar_x, pos_info_tracking_y = calc_relations()
            current_cols = curses.COLS
            current_lines = curses.LINES

        draw_grid()
        display_mode()

        mode = mode_list[current_mode]
        if mode == 'tracking':

            for x in range(NUM_COLS):
                for y in range(NUM_ROWS):
                    prob = round(prob_sum(x,y), 3)
                    if prob > 0.2:
                        tilefill(x,y, colors["BG_MAGENTA"])
                    elif prob > 0.1:
                        tilefill(x,y, colors["BG_BLUE"])
                    elif prob > 0.0:
                        tilefill(x,y, colors["BG_YELLOW"])

            tilefill(*current_max, colors["BG_RED"])

            info_trancking()

        infobar()
        fill_grid()

        stdscr.refresh()

        key = stdscr.getkey().lower()

        if key == KEY_SWITCH_MODE:
            stdscr.clear()
            next_mode()
        elif key == KEY_NEXT:
            if mode == 'tracking':
                robot.move()
                t = predict(t, TT)
                current_sensor = robot.read_sensor()
                t = update(t, O, current_sensor)
                t = normalize(t)
                current_max = 0
                max_x, max_y = [0,0]
                for x in range(NUM_COLS):
                    for y in range(NUM_ROWS):
                        sum_t = prob_sum(x,y)
                        if sum_t > current_max:
                            current_max = sum_t
                            max_x, max_y = [x,y]

                current_max = (max_x, max_y)
                iterations_tracking += 1
            elif mode == 'probability headings':
                cycle_headings()


if __name__ == "__main__":
    import curses
    from curses import wrapper
    wrapper(main)
#    main()


