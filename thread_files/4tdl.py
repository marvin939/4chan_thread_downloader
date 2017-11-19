import sys

from thread_files import climan

def main():
    args = climan.CLIMan().parser.parse_args(sys.argv[1:])
    if hasattr(args, 'func'):
        res = args.func(args)
        if res is not None:
            print(res)

if __name__ == '__main__':
    main()