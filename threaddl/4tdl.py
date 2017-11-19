import sys

from threaddl import climan

if __name__ == '__main__':
    args = climan.CLIMan().parser.parse_args(sys.argv[1:])
    if hasattr(args, 'func'):
        res = args.func(args)
        if res is not None:
            print(res)