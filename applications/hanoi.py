#
# towers of hanoi diversion
#
# Author (a) Damon Anton Permezel, 2021
# All bugs revered.
#
from threading import Thread
from time import sleep_ms
import _thread
import aiko
import aiko.button

width = 128
height = 64

cols = [ (int)(0.5*width/3), (int)(1.5*width/3), (int)(2.5*width/3) ]
poles = [height-2, height-2, height-2]
rwid = (int) (width/6 - 3)
nrings = 10
thick = 4
centre = 6

# ring[] element defns:
WID = 0
COL = 1
ROW = 2
rings = []

fly_row = height - nrings*thick - 2

BUTTON_R = 17
BUTTON_L = 16

left_slider = .5
right_slider = .5

ol = aiko.oled.oleds[1]

hanoi_pause = False

def ring_init(r, nr):
    rings.append([centre+r+1, cols[0], fly_row])
    pass

def ring_draw(r, how):
    wid = r[WID]
    col = r[COL]
    row = r[ROW]
    for i in range(0, thick):
        ol.hline(col-wid-1, row-i, wid+1+wid, how)
        pass
    if how == 0:
	for c in cols:
	    if c == col:
		ol.vline(col, fly_row+1, height - fly_row - 1, 1)
		pass
	    pass
	pass
    ol.show()
    sleep_ms(10 + (int)(left_slider*10))
    pass

def accel(delta):
    if delta > 16: delta >>= 1
    elif delta > 8: delta = 8
    elif delta > 4: delta = 4
    elif delta > 2: delta = 2

    return delta

def ring_up(r, row):
    while r[ROW] > row:
	delta = accel(r[ROW] - row)
        ring_draw(r, 0)
        r[ROW] -= delta
        ring_draw(r, 1)
        pass
    pass

def ring_down(r, row, slow=False):
    while r[ROW] < row:
	delta = row - r[ROW]
        if slow:
	    if delta > thick: delta = thick
	else:
	    delta = accel(delta)
            pass
        ring_draw(r, 0)
        r[ROW] += delta
        ring_draw(r, 1)
        pass
    pass

def ring_left(r, col):
    while col < r[COL]:
	delta = accel(r[COL] - col)
        ring_draw(r, 0)
        r[COL] -= delta
        ring_draw(r, 1)
        pass
    pass

def ring_right(r, col):
    while r[COL] < col:
	delta = accel(col - r[COL])
	ring_draw(r, 0)
	r[COL] += delta
	ring_draw(r, 1)
	pass
    pass
    
def move_ring(n, src, dst):
    global hanoi_pause

    r = rings[n]
    ring_up(r, fly_row)
    poles[src] += thick

    ring_right(r, cols[dst])
    ring_left(r, cols[dst])

    ring_down(r, poles[dst])
    poles[dst] -= thick

    sleep_ms(10 + (int)(right_slider*1000))

    # pause when BUTTON_R is toggled
    while hanoi_pause:
        ol.fill_rect(0, 8, 128, 8, 0)
        ol.text("Hanoi paused.", 0, 8)
        sleep_ms(1000)
        pass
    pass

def place_ring(n):
    r = rings[n]
    row = poles[0]
    ring_down(r, row, True)
    poles[0] -= thick
    ol.show()
    pass

def hanoi_init(n):
    global rings, poles, fly_row
    rings = []
    poles = [height-2, height-2, height-2]

    ol.fill(0)
    ol.show()
    ol.hline(0, height-1, width, 1)

    fly_row = height - n*thick - 2

    for col in cols: ol.vline(col, fly_row+1, height - fly_row - 1, 1)
    for r in range(-1, n-1):
	ring_init(r, n)
        pass
    for r in range(n-1, -1, -1):
	place_ring(r)
	pass
    pass

def _hanoi(n, src, dst, wrk):
    if n > 0: _hanoi(n-1, src, wrk, dst)
    move_ring(n, src, dst)
    if n > 0: _hanoi(n-1, wrk, dst, src)
    pass

def hanoi(n):
    if n > 0 and n <= nrings:
	hanoi_init(n)
	sleep_ms(300)
	_hanoi(n-1, 0, 1, 2)
	pass
    else:
	raise Exception("Funny number of rings:", n)
	pass
    pass

def hanoi_thread():
    hanoi(nrings)
    while True:
        for n in range(2, nrings):
            hanoi(n+1)
        pass
    pass

def slider_handler(number, state, value):
    # print("Slider {}: {} {}".format(number, state, value))
    global left_slider, right_slider

    if state == 1:
        if value < 0: value = 0
        if value > 100: value = 100
        value = 100 - value
        value /= 100

        if number == 12:
	    left_slider = value
        elif number == 14:
	    right_slider = value
	    pass
        pass

    ol.fill_rect(0, 8, 128, 8, 0)
    ol.text("{}% {}%".format(left_slider, right_slider), 0, 8)
    pass
    
def button_handler(number, state):
    global hanoi_pause

    # print("Button {}: {}".format(number, "press" if state else "release"))
    if number == BUTTON_L:
	hanoi_pause = False
    elif number == BUTTON_R:
        hanoi_pause = True
    pass
    ol.fill_rect(0, 8, 128, 8, 0)
    if hanoi_pause:
	ol.text("Paused", 0, 8)
        pass
    pass

def initialise():
    aiko.button.initialise()
    aiko.button.add_slider_handler(slider_handler, 12, 15)
    aiko.button.add_slider_handler(slider_handler, 14, 27)

    aiko.button.add_button_handler(button_handler, [BUTTON_L, BUTTON_R])

    #
    # We need more stack space or else we bomb on small recursion
    #
    _thread.stack_size(8*1024)
    Thread(target=hanoi_thread).start()
    pass
