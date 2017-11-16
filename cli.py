import json
import os
import argparse
from retriever import *
import enum


# DEFAULT_DIRECTORY =
PROGRAM_NAME = '4tdl.py'


class CLIParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                              description='Downloads a thread from 4Chan using URL or an HTML locally.')
        self.parser.add_argument('-d', '--directory',
                                 nargs='?',
                                 help="Destination directory of the thread's contents")
        mutual_group = self.parser.add_mutually_exclusive_group()
        mutual_group.add_argument('url',
                                  type=str,
                                  nargs='?',
                                  help="URL/location of the thread to be downloaded.")
        mutual_group.add_argument('-s', '--synchronise',
                                  action='store_true',
                                  default=False,
                                  help='Synchronise recently downloaded threads, or specified thread folder (with -d)')

    def parse_str(self, input_str):
        cli_input = input_str.split()
        return self.parser.parse_args(cli_input)


class Program:
    CONFIG_NAME = '.4tdl_conf'
    CONFIG_DIR = os.path.expanduser('~')

    # Settings that can be overwritten by loading a config
    DEFAULT_DOWNLOAD_DIR = os.path.expanduser('~/Downloads/4threads/')
    DEFAULT_MAX_RECENT_THREADS = 10

    # Settings name
    OPTION_NAME_DOWNLOAD_DIR = 'default_download_directory'
    OPTION_NAME_MAX_RECENT_THREADS = 'max_recent_threads'
    OPTION_NAME_RECENT_THREADS = 'recent_threads'

    class State(enum.IntEnum):
        DOWNLOAD_TO_DEFAULT = 1
        DOWNLOAD_TO_DIRECTORY = 2
        SYNCHRONISE_RECENT = 5
        SYNCHRONISE_DIRECTORY = 6
        IDLE = 100

    def __init__(self, parsed=None, load_config=False):
        self.download_destination = None
        self.links_retriever = None
        self.synchronise = False
        self.synchronise_recent = False
        # self.state = None

        self.recent_threads = []

        if parsed is not None:
            self.configure_from_parsed(parsed)
        if load_config:
            self.reload_config()

    def reload_config(self):
        self.set_config(self.load_json_dict(self.config_path()))

    def configure_from_parsed(self, parsed):
        """
        Configure this object's variables using a parsed object from an ArgumentParser
        :param parsed:
        :return:
        """
        if hasattr(parsed, 'synchronise'):
            self.synchronise = parsed.synchronise
        if hasattr(parsed, 'url') and parsed.url is not None:
            self.links_retriever = LinksRetriever(parsed.url)
        if hasattr(parsed, 'directory') and parsed.directory is not None:
            self.download_destination = parsed.directory

    @property
    def state(self):
        """
        Return the current state of the program object based on its own attributes
        :return:
        """
        if self.download_destination is not None:
            if self.links_retriever is not None:
                return self.State.DOWNLOAD_TO_DIRECTORY
            if self.synchronise:
                return self.State.SYNCHRONISE_DIRECTORY
        else:
            if self.links_retriever is not None:
                return self.State.DOWNLOAD_TO_DEFAULT
            if self.synchronise:
                return self.State.SYNCHRONISE_RECENT
        return self.State.IDLE

    # def generate_dir_name(self):
    #     return self.

    def load_json_dict(self, config_path=None):
        config = None
        with open(self.config_path()) as f:
            config = json.load(f)
        return config

    def set_config(self, json_dict):
        self.DEFAULT_DOWNLOAD_DIR = json_dict[self.OPTION_NAME_DOWNLOAD_DIR]
        self.DEFAULT_MAX_RECENT_THREADS = json_dict[self.OPTION_NAME_MAX_RECENT_THREADS]
        self.recent_threads = json_dict[self.OPTION_NAME_RECENT_THREADS]

    def config_path(self):
        return os.path.join(self.CONFIG_DIR, self.CONFIG_NAME)

    def save_config(self):
        json_dict = dict()
        json_dict[self.OPTION_NAME_DOWNLOAD_DIR] = self.DEFAULT_DOWNLOAD_DIR
        json_dict[self.OPTION_NAME_MAX_RECENT_THREADS] = self.DEFAULT_MAX_RECENT_THREADS
        json_dict[self.OPTION_NAME_RECENT_THREADS] = self.recent_threads

        with open(self.config_path(), 'w') as f:
            json.dump(json_dict, f)

    @property
    def url(self):
        return self.links_retriever.thread_url

    @property
    def thread_id(self):
        return self.links_retriever.thread_id

    @property
    def thread_title(self):
        return self.links_retriever.title

    def start(self, download=True, write_config=True):
        # if self.links_retriever is None:
        #     raise ValueError('links_retriever is None! Have you called configure_from_parsed?')
        downloader = None
        add_to_recent = False

        if self.state is self.State.DOWNLOAD_TO_DIRECTORY:
            add_to_recent = True
            downloader = BatchDownloader.from_directory(self.download_destination)
            if downloader.links_retriever.thread_is_dead():
                add_to_recent = False
        elif self.state is self.State.SYNCHRONISE_DIRECTORY:
            add_to_recent = True
            downloader = BatchDownloader.from_directory(self.download_destination)
            if downloader.links_retriever.thread_is_dead():
                add_to_recent = False
        elif self.state is self.State.SYNCHRONISE_RECENT:
            pass
        elif self.state is self.State.DOWNLOAD_TO_DEFAULT:
            pass

        if downloader and download:
            downloader.start_download()

        if add_to_recent:
            self.recent_threads += [self.download_destination]

        if write_config:
            # self.recent_threads = list([thread for thread in self.recent_threads if BatchDownloader.from_directory(thread).links_retriever.thread_is_dead()])
            self.save_config()
