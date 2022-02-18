import argparse

from resources import Strings


def print_hi(name):

    parser = argparse.ArgumentParser(description=Strings.HELP_DESC)

    # Adding optional argument
    parser.add_argument("-r", "--Reset", action='store_true', help=Strings.ARG_RESET_HELP)
    parser.add_argument("--NUKE", action='store_true', help=Strings.ARG_NUKE_HELP)

    # Read the args
    args = parser.parse_args()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
