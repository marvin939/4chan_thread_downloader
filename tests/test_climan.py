from cli import Program
from tests.constants import *
from climan import *
import unittest


class CLIManTestCase(unittest.TestCase):
    def setUp(self):
        self.climan = CLIMan()
        # self.climan.print_help()
        self.climan.parser.print_help()

    # def test_parse_mode(self):
    #     # cli_input = 'download {url}'.format(url=STICKY_THREAD_URL)
    #     cli_input = 'download'
    #     args = self.climan.parse_string(cli_input)
    #     self.assertEqual(args.mode, cli_input)
        # self.assertEqual(args.url, STICKY_THREAD_URL)

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
        self.assertEqual(args.dir, TMP_DIRECTORY)

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
        self.assertEqual(args.dir, TMP_DIRECTORY)

    def test_mode_syncdir_using_sync_alias(self):
        cli_input = 'sync {dir}'.format(dir=TMP_DIRECTORY)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.dir, TMP_DIRECTORY)
        # print('Args:', args)

    def test_mode_syncrecent(self):
        cli_input = 'sync-recent'
        with self.assertRaises(NotImplementedError):
            args = self.climan.parse_string(cli_input)
            args.func(args)

    def test_mode_setting_view_option_value(self):
        # alias
        max_recent = Program.OPTION_NAME_MAX_RECENT_THREADS

        cli_input = 'setting {option}'.format(option=max_recent)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.option_name, max_recent)

    def test_mode_settings_change_option(self):
        max_recent = Program.OPTION_NAME_MAX_RECENT_THREADS
        new_val = 20

        cli_input = 'setting {opt} {val}'.format(opt=max_recent, val=new_val)
        args = self.climan.parse_string(cli_input)
        self.assertEqual(args.option_name, max_recent)
        self.assertEqual(int(args.option_value), new_val)   # need to case in int since it's string


    # def test_mode_syncrecent(self):
    #     cli_input = 'sync-recent'
    #     args = self.climan.parse_string(cli_input)
    #     self.assertTrue(args.sync_recent)


# Testing other argparse functionality.
#     def test_hi_arg(self):
#         cli_input = '--hi'
#         args = self.climan.parse_string(cli_input)
#
#     def test_higher_arg(self):
#         cli_input = '--hi wassup'
#         args = self.climan.parse_string(cli_input)
#
#     def test_higher_arg_b(self):
#         cli_input = '--hi "wassup man!"'
#         args = self.climan.parse_string(cli_input)