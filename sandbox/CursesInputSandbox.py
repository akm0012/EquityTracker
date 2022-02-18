import curses
from curses import wrapper
import time


def main(stdscr):
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
    CYAN_AND_MAGENTA = curses.color_pair(1)
    GREEN_AND_WHITE = curses.color_pair(2)

    stdscr.nodelay(True)

    x, y = 0, 0

    while True:
        try:
            key = stdscr.getkey()  # -> "a", "SHIFT", etc.
        except:
            # This will let the program continue to run and not hang and wait for user input
            key = None
        # stdscr.addstr(5, 5, f'Key: {key}')

        if key == "KEY_LEFT":
            x -= 1
        elif key == "KEY_RIGHT":
            x += 1
        elif key == "KEY_UP":
            y -= 1
        elif key == "KEY_DOWN":
            y += 1

        stdscr.clear()
        stdscr.addstr(y, x, "X", CYAN_AND_MAGENTA)
        stdscr.refresh()

    # stdscr.getch()

wrapper(main)
