import sys

from thread_files import climan

def main():
    cli = climan.CLIMan()
    args = cli.parser.parse_args(sys.argv[1:])
    if hasattr(args, 'func'):
        res = args.func(args)
        if res is not None:
            print(res)
    else:
        cli.parser.print_help()

if __name__ == '__main__':
    main()