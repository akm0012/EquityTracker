import argparse

from prod.repository.ConfigRepository import ConfigRepository
from prod.resources import Strings


class Main:

    config_repo = ConfigRepository()

    def process_arguments(self):
        parser = argparse.ArgumentParser(description=Strings.HELP_DESC)

        # Adding optional argument
        parser.add_argument("-r", "--Reset", action='store_true', help=Strings.ARG_RESET_HELP)
        parser.add_argument("--NUKE", action='store_true', help=Strings.ARG_NUKE_HELP)

        args = parser.parse_args()

        if args.Reset:
            self.config_repo.clear_stocks()
            print("Reset!")

        return args


if __name__ == '__main__':
    Main().process_arguments()
    print("Done!")







