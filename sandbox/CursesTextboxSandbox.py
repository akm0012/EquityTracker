import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
import time


def main(stdscr):
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
    CYAN_AND_MAGENTA = curses.color_pair(1)
    GREEN_AND_WHITE = curses.color_pair(2)

    win = curses.newwin(3, 18, 2, 2)
    box = Textbox(win)
    rectangle(stdscr, 1, 1, 5, 20)

    stdscr.refresh()

    box.edit()
    text = box.gather().strip().replace("\n", "")
    stdscr.addstr(10, 40, text)

    stdscr.getch()

wrapper(main)
