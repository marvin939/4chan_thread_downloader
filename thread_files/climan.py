import argparse
import json
import os

from thread_files.retriever import BatchDownloader, LinksRetriever

from thread_files import utilities


# class CLIMan(argparse.ArgumentParser):
class CLIMan:
    DEBUG = False   # For preventing unnecessary downloads during tests
    PROGRAM_NAME = 'thread_files.py'

    COMMAND_SYNC_DIR = 'sync-dir'
    COMMAND_SYNC_RECENT = 'sync-recent'
    COMMAND_DOWNLOAD = 'download'
    COMMAND_SETTING = 'setting'

    CONFIG_NAME = '.4tdl_settings.json'
    CONFIG_DIR = os.path.expanduser('~')

    # Settings that can be overwritten by loading a config
    DEFAULT_DOWNLOAD_DIR = os.path.abspath(os.path.expanduser('~/Downloads/4threads/'))
    DEFAULT_MAX_RECENT_THREADS = 20

    # Settings name
    OPTION_DOWNLOAD_DIR = 'default_download_directory'
    OPTION_MAX_RECENT_THREADS = 'max_recent_threads'
    OPTION_RECENT_THREADS = 'recent_threads'
    SETTINGS = (OPTION_DOWNLOAD_DIR, OPTION_MAX_RECENT_THREADS, OPTION_RECENT_THREADS)

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog=self.PROGRAM_NAME)
        self.url = None
        self.destination = None
        self.mode = None
        self.setting = None
        self.setting_val = None
        self.recent_threads = []

        mode_sub_parser = self.parser.add_subparsers(title='mode',
                                                     dest='mode',  # for determining mode through namespace
                                                     description='Set the action this program will carry out',
                                                     help='''Mode of operation. Follow a sub-command (eg. download) 
                                                     with -h to view more info about it.''')

        # Download sub-command
        download_parser = mode_sub_parser.add_parser(self.COMMAND_DOWNLOAD,
                                                     help='Download a URL and optionally to a directory.')
        download_parser.add_argument('url',
                                     help="Thread's URL to download")
        download_parser.add_argument('--dir', '-d', type=os.path.abspath,
                                     help='Destination directory')
        download_parser.set_defaults(func=self.cli_download_to_directory)

        # Synchronise directory sub-command
        sync_dir_parser = mode_sub_parser.add_parser(self.COMMAND_SYNC_DIR,
                                                     help='syncdir sub-command help',
                                                     aliases=['sync', 'syncdir'])
        sync_dir_parser.add_argument('dir',
                                     type=os.path.abspath,
                                    help='Directory of thread to synchronise')
        sync_dir_parser.set_defaults(func=self.cli_synchronise_to_directory)

        # Synchronise recent sub-command
        sync_recent_parser = mode_sub_parser.add_parser(self.COMMAND_SYNC_RECENT,
                                                        help='Synchronise recently used thread folders.')
        sync_recent_parser.set_defaults(func=self.cli_synchronise_recent_threads)

        # Setting sub-command
        setting_parser = mode_sub_parser.add_parser(self.COMMAND_SETTING,
                                                    help='Modify/view downloader settings')
        setting_parser.add_argument('option_name', type=str, help='Option name', choices=self.SETTINGS)
        setting_parser.add_argument('option_value', nargs='?', help='New value of option')
        setting_parser.set_defaults(func=self.cli_settings)

        self.reload_config()

    def parse_string(self, args_string):
        """
        Wrapper for ArgumentParser's parse_args to automatically split string options.
        :param args_string: String containing arguments passed via command line
        :return: Namespace object containing the parsed command line arguments
        """
        return self.parser.parse_args(args=args_string.split())

    def cli_settings(self, args):
        if args.option_name == self.OPTION_MAX_RECENT_THREADS:
            if args.option_value is not None:
                self.DEFAULT_MAX_RECENT_THREADS = int(args.option_value)
            else:
                return self.DEFAULT_MAX_RECENT_THREADS
        elif args.option_name == self.OPTION_DOWNLOAD_DIR:
            if args.option_value is not None:
                self.DEFAULT_DOWNLOAD_DIR = str(args.option_value)
            else:
                return self.DEFAULT_DOWNLOAD_DIR
        '''Don't bother with modification of recent threads.'''

        self.save_config()
        return

    def cli_synchronise_recent_threads(self, args):
        pop_list = set()
        for thread_dir in self.recent_threads:
            if not os.path.exists(thread_dir):
                pop_list.add(thread_dir)
                continue

            downloader = BatchDownloader.from_directory(thread_dir)
            self.downloader_start(downloader)
            if downloader.links_retriever.thread_is_dead():
                pop_list.add(thread_dir)
                # pop_list += [thread_dir]

        self.recent_threads = list((os.path.abspath(thread_dir) for thread_dir in self.recent_threads if thread_dir not in pop_list))
        self.save_config()

        return self.recent_threads

    def cli_synchronise_to_directory(self, args):
        downloader = BatchDownloader.from_directory(args.dir)
        self.downloader_start(downloader)
        self.recent_threads_add(downloader)
        self.save_config()
        return downloader.destination_folder
        # pass

    def downloader_start(self, downloader):
        downloader.DEBUG = self.DEBUG
        downloader.start_download()

    def cli_download_to_directory(self, args):
        """
        Start downloading thread using a namespace arg
        :param args: Namespace
        :return: string containing destination folder of downloaded thread
        """
        links_retriever = LinksRetriever(args.url)

        if args.dir is None:
            thread_dir = os.path.join(self.DEFAULT_DOWNLOAD_DIR,
                                      links_retriever.board_initials,
                                      links_retriever.thread_id)
            args.dir = thread_dir

        downloader = BatchDownloader(links_retriever, args.dir)
        self.downloader_start(downloader)
        self.recent_threads_add(downloader)
        self.save_config()

        return downloader.destination_folder

    def recent_threads_add(self, downloader):
        """
        Determines if the current BatchDownloader's destination folder should be added to recent threads.
        :param downloader: BatchDownloader object
        :return: None
        """
        if downloader.links_retriever.thread_is_dead():
            return
        if downloader.destination_folder in self.recent_threads:
            return
        if len(self.recent_threads) == self.DEFAULT_MAX_RECENT_THREADS:
            self.recent_threads = self.recent_threads[1:]   # Shift left
        self.recent_threads += [os.path.abspath(os.path.expanduser(downloader.destination_folder))]

    @staticmethod
    def config_path():
        """Return config file's path using CLIMan's CONFIG_DIR and CONFIG_NAME values"""
        return os.path.join(CLIMan.CONFIG_DIR, CLIMan.CONFIG_NAME)

    def save_config(self):
        settings_dict = {self.OPTION_DOWNLOAD_DIR: self.DEFAULT_DOWNLOAD_DIR,
                         self.OPTION_MAX_RECENT_THREADS: self.DEFAULT_MAX_RECENT_THREADS,
                         self.OPTION_RECENT_THREADS: self.recent_threads}
        with open(self.config_path(), 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f)

    # @staticmethod
    # def load_json(path):
    #     # json_obj = None
    #     with open(path, encoding='utf-8') as f:
    #         json_obj = json.load(f)
    #     return json_obj

    def configure(self, config_dict):
        """
        Load settings using a dictionary object containing keys from CLIMan.SETTINGS
        :param config_dict: Dictionary object
        :return:
        """
        settings_set = set(self.SETTINGS)
        config_keys_set = set(config_dict.keys())
        if config_keys_set.intersection(settings_set) != settings_set:
            raise KeyError('config_dict argument doesn\'t contain the necessary keys: {}'.format(settings_set - config_keys_set))

        self.DEFAULT_DOWNLOAD_DIR = config_dict[self.OPTION_DOWNLOAD_DIR]
        self.DEFAULT_MAX_RECENT_THREADS = config_dict[self.OPTION_MAX_RECENT_THREADS]
        self.recent_threads = config_dict[self.OPTION_RECENT_THREADS]

    def reload_config(self):
        if not os.path.exists(self.config_path()):
            return
        self.configure(utilities.json_from_path(self.config_path()))
