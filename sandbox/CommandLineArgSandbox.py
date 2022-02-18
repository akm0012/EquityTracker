import argparse
from prod.resources import Strings

parser = argparse.ArgumentParser(description=Strings.HELP_DESC)

# Adding optional argument
parser.add_argument("-r", "--Reset", action='store_true', help=Strings.ARG_RESET_HELP)
parser.add_argument("--NUKE", action='store_true', help=Strings.ARG_NUKE_HELP)

# Read the args
args = parser.parse_args()

# if args.Output:
#     print("Displaying Output as: % s" % args.Output)
