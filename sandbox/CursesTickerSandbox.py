import curses
from curses import wrapper
import time


def main(stdscr):
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
    CYAN_AND_MAGENTA = curses.color_pair(1)
    GREEN_AND_WHITE = curses.color_pair(2)

    height = curses.LINES - 1
    width = curses.COLS - 1

    pad = curses.newpad(100, width)
    stdscr.refresh()

    for i in range(100):
        for j in range(26):
            char = chr(67 + j)
            pad.addstr(char, CYAN_AND_MAGENTA)

    for i in range(50):
        stdscr.clear()
        stdscr.refresh()
        pad.refresh(0, 0, 5, i, 10, width)
        time.sleep(0.2)

    stdscr.getch()

wrapper(main)
