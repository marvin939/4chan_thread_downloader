import os
import unittest
from tempfile import TemporaryDirectory

from thread_files.climan import CLIMan
from thread_files.retriever import BatchDownloader, LinksRetriever

# from cli import Program
from tests.constants import *
from tests.useful import create_test_environment


class CLIManArgumentParsingTestCase(unittest.TestCase):
    def setUp(self):
        self.climan = CLIMan()
        # self.climan.print_help()
        # self.climan.parser.print_help()

    def test_mode_download(self):
        cli_input = 'download {url}'.format(url=STICKY_THREAD_URL)
        args = self.climan.parse_string(cli_input)
        print('args:', args)
        self.assertEqual(args.url, STICKY_THREAD_URL)

    def test_mode_download_no_url(self):
        cli_input = 'download'
        with self.assertRaises(SystemExit):
            args = self.climan.parse_string(cli_input)

    def test_mode_download_to_directory(self):
        cli_input = 'download {url} -d {dir}'.format(url=STICKY_THREAD_URL, dir=TMP_DIRECTORY)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.url, STICKY_THREAD_URL)
        self.assertEqual(args.dir, os.path.abspath(TMP_DIRECTORY))

    def test_mode_download_dir_none(self):
        """Check if parser's return object has dir property even if it was not set in the first place"""
        cli_input = 'download {url}'
        args = self.climan.parse_string(cli_input)
        self.assertTrue(hasattr(args, 'dir'))
        print('Dir:', args.dir)

    def test_mode_syncdir_dir_none(self):
        cli_input = 'syncdir'
        with self.assertRaises(SystemExit):
            args = self.climan.parse_string(cli_input)

    def test_mode_syncdir_with_dir(self):
        cli_input = 'syncdir {dir}'.format(dir=TMP_DIRECTORY)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.dir, os.path.abspath(TMP_DIRECTORY))

    def test_mode_syncdir_using_sync_alias(self):
        cli_input = 'sync {dir}'.format(dir=TMP_DIRECTORY)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.dir, os.path.abspath(TMP_DIRECTORY))
        # print('Args:', args)

    def test_mode_setting_view_option_value(self):
        # alias
        max_recent = CLIMan.OPTION_MAX_RECENT_THREADS

        cli_input = 'setting {option}'.format(option=max_recent)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.option_name, max_recent)

    def test_mode_settings_change_option(self):
        """Test parsed new value after changing a setting"""
        max_recent = CLIMan.OPTION_MAX_RECENT_THREADS
        new_val = 20

        cli_input = 'setting {opt} {val}'.format(opt=max_recent, val=new_val)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.option_name, max_recent)
        self.assertEqual(int(args.option_value), new_val)   # need to case in int since it's string

    def test_mode_settings_option_choices(self):
        """Test that the choice parameter works on setting sub-command"""
        cli_inputs = tuple(('{cmd} {opt}'.format(cmd=CLIMan.COMMAND_SETTING, opt=option) for option in CLIMan.SETTINGS))
        for cli_input in cli_inputs:
            with self.subTest():
                args = self.climan.parse_string(cli_input)
                self.assertIn(args.option_name, CLIMan.SETTINGS)

    def test_mode_settings_invalid_choice(self):
        cli_input = '{cmd} potaters'.format(cmd=CLIMan.COMMAND_SETTING)
        with self.assertRaises(SystemExit):
            args = self.climan.parse_string(cli_input)


class CLIManLoadSetSaveConfig(unittest.TestCase):
    def setUp(self):
        self.temp_config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.temp_download_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        CLIMan.CONFIG_DIR = self.temp_config_dir.name
        CLIMan.DEFAULT_DOWNLOAD_DIR = self.temp_download_dir.name
        self.climan = CLIMan()

        # Create a config file at temp_config_dir
        self.climan.save_config()

    def test_config_path(self):
        self.assertEqual(CLIMan.config_path(), os.path.join(CLIMan.CONFIG_DIR, CLIMan.CONFIG_NAME))

    def test_save_config_file_exists(self):
        self.climan.save_config()
        self.assertTrue(os.path.exists(self.climan.config_path()))

    def test_load_json_dict(self):
        """Check if load_json has the right contents stored in it"""
        config_dict = utilities.json_from_path(CLIMan.config_path())
        self.assertIsNotNone(config_dict)
        self.assertEqual(set(CLIMan.SETTINGS), set(config_dict.keys()))

    def test_set_config(self):
        # Constants to replace climan instance's option variables to demonstrate set_config
        ddir = '~/Downloads/t0/'
        maxthreads = 123
        recent_threads = ['~/Downloads/t1', '~/Downloads/t2', '~/Downloads/t3']

        self.climan.DEFAULT_DOWNLOAD_DIR = ddir
        self.climan.DEFAULT_MAX_RECENT_THREADS = maxthreads
        self.climan.recent_threads = recent_threads

        self.climan.configure(utilities.json_from_path(self.climan.config_path()))

        self.assertIsNotNone(self.climan.DEFAULT_DOWNLOAD_DIR)
        self.assertIsNotNone(self.climan.DEFAULT_MAX_RECENT_THREADS)
        self.assertIsNotNone(self.climan.recent_threads)

        self.assertNotEqual(self.climan.DEFAULT_DOWNLOAD_DIR, ddir)
        self.assertNotEqual(self.climan.DEFAULT_MAX_RECENT_THREADS, maxthreads)
        self.assertNotEqual(self.climan.recent_threads, recent_threads)

    def test_set_config_with_missing_keys(self):
        """Make sure that CLIMan's configure function raises KeyError when there are missing keys"""
        config_dict = {'ABC': 123,
                       'DEF': 'GHI'}
        with self.assertRaises(KeyError):
            self.climan.configure(config_dict)

    def test_reload_config_not_load_settings_if_config_is_missing(self):
        os.remove(CLIMan.config_path())

        self.climan.reload_config()
        self.assertEqual(self.climan.DEFAULT_DOWNLOAD_DIR, CLIMan.DEFAULT_DOWNLOAD_DIR)
        self.assertEqual(self.climan.DEFAULT_MAX_RECENT_THREADS, CLIMan.DEFAULT_MAX_RECENT_THREADS)
        self.assertEqual(self.climan.recent_threads, [])


class CLIManAutoLoadsConfig(unittest.TestCase):
    def setUp(self):
        self.temp_config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.original_max_recent_threads = int(CLIMan.DEFAULT_MAX_RECENT_THREADS)
        self.new_max = 99
        CLIMan.CONFIG_DIR = self.temp_config_dir.name

        # Create config
        self.climan = CLIMan()
        self.climan.DEFAULT_MAX_RECENT_THREADS = self.new_max # Replace it since it's going to be saved
        self.climan.save_config()

        self.climan = CLIMan()  # Force reload config

    def test_auto_load_config(self):
        """Ensure that the CLIMan instance automatically loads its settings upon instantiation"""
        self.assertEqual(self.climan.DEFAULT_MAX_RECENT_THREADS, self.new_max)


class CLIManDownloadSubCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.download_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        CLIMan.CONFIG_DIR = self.config_dir.name
        CLIMan.DEBUG = True
        self.climan = CLIMan()
        self.input_format = '{subcmd} {url} -d {dir}'
        self.cli_input = self.input_format.format(subcmd=CLIMan.COMMAND_DOWNLOAD, url=THREAD_URL,
                                                  dir=self.download_dir.name)
        self.climan.save_config()

    def test_download_to_directory_sub_command(self):
        args = self.climan.parse_string(self.cli_input)
        # print('type of args:', type(args))

        self.assertEqual(args.func, self.climan.cli_download_to_directory)
        downloaded_dir = args.func(args)

        thread_details_path = os.path.join(downloaded_dir, BatchDownloader.THREAD_DETAILS_FILENAME)
        self.assertTrue(os.path.exists(thread_details_path))

    def test_download_to_directory_added_to_recent_threads(self):
        args = self.climan.parse_string(self.cli_input)
        thread_dir = args.func(args)
        self.assertIn(thread_dir, self.climan.recent_threads)

    def test_dead_thread_added_to_recent(self):
        """Dead threads should not be added to recent threads variable"""
        cli_input = self.input_format.format(subcmd=CLIMan.COMMAND_DOWNLOAD, url=TEST_THREAD_FILENAME, dir=self.download_dir.name)
        args = self.climan.parse_string(cli_input)
        thread_dir = args.func(args)
        self.assertNotIn(thread_dir, self.climan.recent_threads)

    def test_config_updated_after_download(self):
        cli_input = self.input_format.format(subcmd=CLIMan.COMMAND_DOWNLOAD, url=STICKY_THREAD_URL,
                                             dir=self.download_dir.name)
        args = self.climan.parse_string(cli_input)
        thread_dir = args.func(args)
        config_dict = utilities.json_from_path(self.climan.config_path())
        self.assertIn(thread_dir, config_dict[CLIMan.OPTION_RECENT_THREADS])


class CLIManDownloadDirectoryDefaultGenerate(unittest.TestCase):
    def setUp(self):
        self.default_download_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        CLIMan.DEBUG = True
        CLIMan.CONFIG_DIR = self.config_dir.name
        CLIMan.DEFAULT_DOWNLOAD_DIR = self.default_download_dir.name
        self.climan = CLIMan()

    def test_download_thread_default_directory(self):
        """CLIMan with download command and no specified directory will generate a new directory based on
        the board initials and thread ID of the thread to be downloaded."""
        cli_input = '{subcmd} {url}'.format(subcmd=CLIMan.COMMAND_DOWNLOAD, url=TEST_THREAD_FILENAME)
        print('cli_input:', repr(cli_input))
        args = self.climan.parse_string(cli_input)
        self.assertIsNone(args.dir)

        thread_dir = args.func(args)
        self.assertIsNotNone(thread_dir)
        print('thread_dir:', thread_dir)

        details_path = os.path.join(thread_dir, BatchDownloader.THREAD_DETAILS_FILENAME)
        self.assertTrue(os.path.exists(details_path))


class CLIManSyncDirSubCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.thread_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        CLIMan.CONFIG_DIR = self.config_dir.name
        CLIMan.DEBUG = True
        self.climan = CLIMan()
        self.input_format = '{subcmd} {dir}'
        self.cli_input = self.input_format.format(subcmd=CLIMan.COMMAND_SYNC_DIR, dir=self.thread_dir.name)
        self.climan.save_config()

        create_test_environment(self.thread_dir.name)

    def test_synchronise_directory(self):
        args = self.climan.parse_string(self.cli_input)
        self.assertEqual(args.func, self.climan.cli_synchronise_to_directory)
        downloaded_dir = args.func(args)

        # Check details pickle existence
        thread_details_path = os.path.join(downloaded_dir, BatchDownloader.THREAD_DETAILS_FILENAME)
        self.assertTrue(os.path.exists(thread_details_path))

    def test_synchronise_directory_added_to_recent_threads(self):
        create_test_environment(self.thread_dir.name, url=STICKY_THREAD_URL)
        args = self.climan.parse_string(self.cli_input)
        thread_dir = args.func(args)
        self.assertIn(thread_dir, self.climan.recent_threads)

    def test_dead_thread_added_to_recent(self):
        """Dead threads should not be added to recent threads variable"""
        args = self.climan.parse_string(self.cli_input)
        thread_dir = args.func(args)
        self.assertNotIn(thread_dir, self.climan.recent_threads)

    def test_config_updated_after_download(self):
        create_test_environment(self.thread_dir.name, url=STICKY_THREAD_URL)

        args = self.climan.parse_string(self.cli_input)
        thread_dir = args.func(args)
        config_dict = utilities.json_from_path(self.climan.config_path())
        self.assertIn(thread_dir, config_dict[CLIMan.OPTION_RECENT_THREADS])


class CLIManSyncRecentTestCase(unittest.TestCase):
    """Test sync-recent sub-command"""

    def setUp(self):
        self.dead_thread_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.alive_thread_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        CLIMan.CONFIG_DIR = self.config_dir.name
        CLIMan.DEBUG = True
        self.climan = CLIMan()
        self.input_format = '{subcmd} {dir}'
        self.cli_input = CLIMan.COMMAND_SYNC_RECENT

        create_test_environment(self.dead_thread_dir.name, url=TEST_THREAD_FILENAME)   # Creates a dead thread
        # Pretend that the dead thread is still alive
        create_test_environment(self.alive_thread_dir.name, url=STICKY_THREAD_URL)
        self.climan.recent_threads += [self.dead_thread_dir.name, self.dead_thread_dir.name, self.dead_thread_dir.name,
                                       self.dead_thread_dir.name, self.alive_thread_dir.name]
        self.climan.save_config()   # For loading purposes later

    def test_correct_default_function(self):
        args = self.climan.parse_string(self.cli_input)
        self.assertEqual(args.func, self.climan.cli_synchronise_recent_threads)

    def test_sync_recent(self):
        cli_input = CLIMan.COMMAND_SYNC_RECENT
        args = self.climan.parse_string(self.cli_input)
        args.func(args)
        self.assertNotIn(self.dead_thread_dir.name, self.climan.recent_threads)
        self.assertIn(os.path.abspath(self.alive_thread_dir.name), self.climan.recent_threads)

    def test_sync_recent_update_config(self):
        args = self.climan.parse_string(self.cli_input)
        args.func(args)
        config_dict = utilities.json_from_path(self.climan.config_path())
        self.assertNotIn(self.dead_thread_dir.name, config_dict[CLIMan.OPTION_RECENT_THREADS])
        self.assertIn(os.path.abspath(self.alive_thread_dir.name), config_dict[CLIMan.OPTION_RECENT_THREADS])

    def test_recent_list_with_missing_threads(self):
        """For when the recent_list contains a thread folder that has already been deleted from the hard drive."""
        dead = self.dead_thread_dir.name
        del self.dead_thread_dir
        self.assertFalse(os.path.exists(dead))
        args = self.climan.parse_string(CLIMan.COMMAND_SYNC_RECENT)
        args.func(args)
        self.assertNotIn(dead, self.climan.recent_threads)
        '''All thread folders that no longer exist should be removed from the list'''


class CLIManMaxRecentThreadsExceeded(unittest.TestCase):
    def setUp(self):
        self.dead_thread_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.alive_thread_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        CLIMan.CONFIG_DIR = self.config_dir.name
        CLIMan.DEBUG = True
        self.climan = CLIMan()
        # dead threads will fill in the recents, since the alive thread will be used as a unique element. The function
        # recent_threads_add doesn't add non-unique elements, so we have to force adding (next line)
        self.climan.recent_threads = [self.dead_thread_dir.name] * self.climan.DEFAULT_MAX_RECENT_THREADS
        print('recent_threads:', self.climan.recent_threads)

    def test_add_recent_exceed(self):
        """The idea is that when the number of recent threads exceed the config's maximum,
        the list pop the first element off, before adding the new one in"""
        self.assertEqual(len(self.climan.recent_threads), self.climan.DEFAULT_MAX_RECENT_THREADS)
        downloader = BatchDownloader(LinksRetriever(STICKY_THREAD_URL), self.alive_thread_dir.name)
        self.climan.recent_threads_add(downloader)

        # Still the same length
        self.assertEqual(len(self.climan.recent_threads), self.climan.DEFAULT_MAX_RECENT_THREADS)

        # The alive thread is the last element
        self.assertEqual(self.climan.recent_threads[-1], os.path.abspath(self.alive_thread_dir.name))


class CLIManSettingSubCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        CLIMan.CONFIG_DIR = self.config_dir.name
        CLIMan.DEBUG = True
        self.climan = CLIMan()
        self.set_format = '{sub} {opt} {val}'
        self.get_format = '{sub} {opt}'

    def test_subcommand_with_option_name_and_value(self):
        '''This test has already been done before'''
        option = CLIMan.OPTION_MAX_RECENT_THREADS
        new_value = 100
        cli_input = self.set_format.format(sub=CLIMan.COMMAND_SETTING, opt=option, val=new_value)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.option_name, CLIMan.OPTION_MAX_RECENT_THREADS)
        self.assertEqual(int(args.option_value), new_value)

    def test_correct_function_returned(self):
        cli_input = self.set_format.format(sub=CLIMan.COMMAND_SETTING, opt=CLIMan.OPTION_MAX_RECENT_THREADS, val=100)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.func, self.climan.cli_settings)

    def test_option_set_max_recent_threads(self):
        cli_input = self.set_format.format(sub=CLIMan.COMMAND_SETTING, opt=CLIMan.OPTION_MAX_RECENT_THREADS,
                                               val=100)
        args = self.climan.parse_string(cli_input)
        args.func(args)
        self.assertEqual(self.climan.DEFAULT_MAX_RECENT_THREADS, int(args.option_value))

    def test_option_get_max_recent_threads(self):
        cli_input = self.get_format.format(sub=CLIMan.COMMAND_SETTING, opt=CLIMan.OPTION_MAX_RECENT_THREADS)
        args = self.climan.parse_string(cli_input)
        new_max = args.func(args)
        self.assertEqual(new_max, self.climan.DEFAULT_MAX_RECENT_THREADS)

    def test_option_set_default_download_dir(self):
        new_download_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        cli_input = self.set_format.format(sub=CLIMan.COMMAND_SETTING, opt=CLIMan.OPTION_DOWNLOAD_DIR,
                                               val=new_download_dir.name)
        args = self.climan.parse_string(cli_input)
        args.func(args)
        self.assertEqual(self.climan.DEFAULT_DOWNLOAD_DIR, new_download_dir.name)

    def test_option_get_default_download_dir(self):
        cli_input = self.get_format.format(sub=CLIMan.COMMAND_SETTING, opt=CLIMan.OPTION_DOWNLOAD_DIR)
        args = self.climan.parse_string(cli_input)
        download_dir = args.func(args)
        self.assertEqual(download_dir, self.climan.DEFAULT_DOWNLOAD_DIR)

    def test_new_settings_get_saved(self):
        self.climan.save_config()   # Force create a new config

        cli_input = self.set_format.format(sub=CLIMan.COMMAND_SETTING, opt=CLIMan.OPTION_MAX_RECENT_THREADS,
                                               val=100)
        args = self.climan.parse_string(cli_input)
        args.func(args)  # internally, change some properties

        # Load the settings and compare
        config_dict = utilities.json_from_path(self.climan.config_path())
        self.assertEqual(config_dict[CLIMan.OPTION_MAX_RECENT_THREADS], int(args.option_value))


class ConvertDirArgsToAbsolutePathTestCase(unittest.TestCase):

    def setUp(self):
        self.climan = CLIMan()

    def test_download_dir_arg_period(self):
        """The dir argument in the download command should turn the '.' into absolute path."""
        args = self.climan.parse_string('download {} -d .'.format(STICKY_THREAD_URL))
        self.assertNotEqual(args.dir, '.')

    def test_syncdir_dir_arg_period(self):
        """The dir argument in the download command should turn the '.' into absolute path."""
        args = self.climan.parse_string('sync-dir .'.format(STICKY_THREAD_URL))
        self.assertNotEqual(args.dir, '.')
