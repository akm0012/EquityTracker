import curses
from curses import wrapper
import time


def main(stdscr):
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
    CYAN_AND_MAGENTA = curses.color_pair(1)
    GREEN_AND_WHITE = curses.color_pair(2)

    # Window size = 1h, 10w.  Location = 10,10
    counter_window = curses.newwin(1, 20, 10, 10)
    stdscr.addstr("Hello World")
    stdscr.refresh()

    for i in range(100):
        counter_window.clear()
        stdscr.clear()

        color = CYAN_AND_MAGENTA
        if i % 2 == 0:
            color = GREEN_AND_WHITE

        counter_window.addstr(f'Count {i}', color)
        counter_window.refresh()
        time.sleep(0.1)

    # stdscr.addstr(10, 10, "Hello World!", curses.A_BOLD)
    # stdscr.addstr(10, 20, "OVERWRITTEN", curses.A_UNDERLINE | CYAN_AND_MAGENTA)
    # stdscr.addstr(1, 1, "This is a color", GREEN_AND_WHITE)
    # stdscr.refresh()
    stdscr.getch()


wrapper(main)
