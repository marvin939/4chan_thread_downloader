import argparse


# class CLIMan(argparse.ArgumentParser):
class CLIMan:
    PROGRAM_NAME = '4tdl.py'

    def __init__(self):
        # super().__init__(prog=self.PROGRAM_NAME)
        self.parser = argparse.ArgumentParser(prog=self.PROGRAM_NAME)
        self.url = None
        self.destination = None
        self.mode = None
        self.setting = None
        self.setting_val = None

        # self.parser.add_argument('mode', help='Mode of operation')
        # self.parser.add_argument('--hi', help='print things!', nargs='?', const='Hi!!!', type=print)
        mode_sub_parser = self.parser.add_subparsers(title='mode',
                                                     dest='mode',   # for determining mode
                                                     description='Set the action this program will carry out',
                                                     help='Mode of operation')

        download_parser = mode_sub_parser.add_parser('download',
                                                     help='download sub-command help')
        download_parser.add_argument('url',
                                     help="Thread's URL to download")
        download_parser.add_argument('--dir', '-d',
                                     help='Destination directory')

        sync_dir_parser = mode_sub_parser.add_parser('syncdir',
                                                     help='syncdir sub-command help',
                                                     aliases=['sync'])
        sync_dir_parser.add_argument('dir',
                                    help='Directory of thread to synchronise')

        sync_recent_parser = mode_sub_parser.add_parser('sync-recent',
                                                       help='Synchronise recently used thread folders.')

        def raise_error(args):
            print('args:', args)
            raise NotImplementedError()
        sync_recent_parser.set_defaults(func=raise_error)   # <-- Use set_defaults with func function arguement
                                                            # to return a callable function
                                                            # and pass the returned Namespace as an argument
        '''
        eg.
        args = self.parser.parse_args('sync-recent')
        args.func(args)
        '''

        setting_parser = mode_sub_parser.add_parser('setting',
                                                    help='Modify/view downloader settings')
        setting_parser.add_argument('option_name', type=str, help='Option name')
        setting_parser.add_argument('option_value', nargs='?', help='New value of option')


    def parse_string(self, args_string):
        return self.parser.parse_args(args=args_string.split())

    # def from_namespace(self, namespace):
    #     self.