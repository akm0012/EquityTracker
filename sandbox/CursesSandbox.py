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

    for i in range(100):
        stdscr.clear()

        color = CYAN_AND_MAGENTA
        if i % 2 == 0:
            color = GREEN_AND_WHITE

        stdscr.addstr(f'Count {i}', color)
        stdscr.addstr(0, 10, f'Height {height}', color)
        stdscr.addstr(0, 20, f'Width {width}', color)

        stdscr.refresh()
        time.sleep(0.1)

    # stdscr.addstr(10, 10, "Hello World!", curses.A_BOLD)
    # stdscr.addstr(10, 20, "OVERWRITTEN", curses.A_UNDERLINE | CYAN_AND_MAGENTA)
    # stdscr.addstr(1, 1, "This is a color", GREEN_AND_WHITE)
    # stdscr.refresh()
    stdscr.getch()


wrapper(main)
