import argparse
from . import Hotline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", default="light")

    args = parser.parse_args()
    hl = Hotline(style=args.style)
    hl.show()


if __name__ == "__main__":
    main()
