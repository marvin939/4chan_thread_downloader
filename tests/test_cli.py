import json
from tests.useful import *
import utilities
from tests.constants import *
import unittest
from retriever import *
from cli import *
from tempfile import TemporaryDirectory


class CliParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = CLIParser()
        self.tempdir = TemporaryDirectory(dir=TMP_DIRECTORY)

    # def tearDown(self):
    #     self.parser.parser.print_help()

    def test_destination_directory(self):
        input = '--directory {}'.format(self.tempdir.name)
        returned = self.parser.parse_str(input)
        self.assertEqual(returned.directory, self.tempdir.name)
        self.assertTrue(os.path.exists(returned.directory))

    # def test_invalid_multiple_destination_directory(self):
    #     input = '--directory {0} {0}'.format(self.tempdir.name)
    #     with self.assertRaises(SystemExit):  # I don't know what type of error...
    #         returned = self.parser.parse(input)

    def test_url(self):
        url = self.tempdir.name
        input = '{0} --directory {1}'.format(url, self.tempdir.name)
        returned = self.parser.parse_str(input)
        self.assertEqual(returned.url, url)

    def test_invalid_multiple_urls(self):
        url = self.tempdir.name
        input = '{0} {0} --directory {1}'.format(url, self.tempdir.name)
        with self.assertRaises(SystemExit):
            returned = self.parser.parse_str(input)
            print('URL returned:', returned.url)

    def test_synchronize_argument(self):
        input = '-s'
        returned = self.parser.parse_str(input)
        self.assertTrue(returned.synchronise)

    def test_synchronize_argument_false(self):
        input = ''  # implicitly state to not synchronize
        returned = self.parser.parse_str(input)
        self.assertFalse(returned.synchronise)

    def test_synchronize_directory(self):
        input = '-sd {}'.format(self.tempdir.name)
        returned = self.parser.parse_str(input)
        self.assertTrue(returned.synchronise)
        self.assertEqual(returned.directory, self.tempdir.name)

    # def test_syncrhonize_recent(self):
    #     # input = '-s recent'
    #     # input = '-sr'
    #     input = '--sync-recent'
    #     returned = self.parser.parse_str(input)
    #     # self.assertTrue(returned.synchronize)
    #     # self.assertTrue(returned.recent)
    #     self.assertTrue(returned.sync_recent)
        """I think i'm better off just using "-s" alone for synchronizing recently downloaded threads"""

    def test_mutual_exclusion_url_and_sync(self):
        input = '{} -s'.format(self.tempdir.name)
        with self.assertRaises(SystemExit):
            returned = self.parser.parse_str(input)


class ProgramCLIArgsTestCase(unittest.TestCase):
    """
    Tests prefixed with:
    test_cli_args - Test Program object attributes using parsed cli arguments
    """

    # def setUp(self):
    #     self.program = Program()

    # @unittest.skip
    def test_cli_args_url_download_default_directory(self):
        cli_input = '{}'.format(TEST_THREAD_FILENAME)
        parsed = CLIParser().parse_str(cli_input)
        program = Program(parsed)
        self.assertIsNotNone(program.links_retriever)
        self.assertEqual(program.state, Program.State.DOWNLOAD_TO_DEFAULT)

    def test_cli_args_url_download_to_directory(self):
        cli_input = '{} -d {}'.format(TEST_THREAD_FILENAME, TMP_DIRECTORY)
        parsed = CLIParser().parse_str(cli_input)
        program = Program(parsed)
        self.assertIsNotNone(program.links_retriever)
        self.assertEqual(program.url, TEST_THREAD_FILENAME)
        self.assertIsNotNone(program.download_destination)
        self.assertEqual(program.download_destination, TMP_DIRECTORY)
        self.assertEqual(program.state, Program.State.DOWNLOAD_TO_DIRECTORY)

    def test_cli_args_url_download_to_directory_but_with_invalid_sync(self):
        cli_input = '{} -sd {}'.format(TEST_THREAD_FILENAME, TMP_DIRECTORY)
        with self.assertRaises(SystemExit):
            parsed = CLIParser().parse_str(cli_input)
            program = Program(parsed)

    def test_cli_args_url_synchronise_to_directory(self):
        cli_input = '-sd {}'.format(TMP_DIRECTORY)
        parsed = CLIParser().parse_str(cli_input)
        program = Program(parsed)
        self.assertTrue(program.synchronise)
        self.assertEqual(program.download_destination, TMP_DIRECTORY)
        self.assertEqual(program.state, Program.State.SYNCHRONISE_DIRECTORY)
        # pass

    def test_cli_args_url_synchronise_recent(self):
        cli_input = '-s'
        parsed = CLIParser().parse_str(cli_input)
        program = Program(parsed)
        self.assertTrue(program.synchronise)
        self.assertIsNone(program.download_destination)
        self.assertEqual(program.state, Program.State.SYNCHRONISE_RECENT)


class ProgramConfigLoadingTestCase(unittest.TestCase):
    ORIGINAL_CONFIG_DIR = Program.CONFIG_DIR
    FAKE_DOWNLOAD_DIR = os.path.join(TMP_DIRECTORY, '1234567890')
    FAKE_MAX_RECENT_THREADS = 20

    def setUp(self):
        self.tmpdir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.tmpdir2 = None
        Program.CONFIG_DIR = self.tmpdir.name
        # create_test_environment(self.tmpdir.name)
        self.create_config_test_environment(self.tmpdir.name)
        self.config_path = os.path.join(Program.CONFIG_DIR, Program.CONFIG_NAME)

    def create_config_test_environment(self, directory):
        config_path = os.path.join(Program.CONFIG_DIR, Program.CONFIG_NAME)
        conf = dict()
        conf[Program.OPTION_NAME_DOWNLOAD_DIR] = self.FAKE_DOWNLOAD_DIR
        conf[Program.OPTION_NAME_MAX_RECENT_THREADS] = self.FAKE_MAX_RECENT_THREADS
        conf[Program.OPTION_NAME_RECENT_THREADS] = []

        # Create dummy recent threads
        self.tmpdir2 = TemporaryDirectory(dir=TMP_DIRECTORY)
        create_test_environment(self.tmpdir2.name)
        for i in range(conf[Program.OPTION_NAME_MAX_RECENT_THREADS]):
            conf[Program.OPTION_NAME_RECENT_THREADS] += [self.tmpdir2.name]

        with open(config_path, 'w') as f:
            json.dump(conf, f)

    def test_default_config_dir_override_success(self):
        self.assertEqual(Program.CONFIG_DIR, self.tmpdir.name)

    def test_create_config_test_environment(self):
        self.assertTrue(os.path.exists(self.config_path))
        conf = None
        with open(self.config_path) as f:
            conf = json.load(f)
        self.assertEqual(conf[Program.OPTION_NAME_DOWNLOAD_DIR], self.FAKE_DOWNLOAD_DIR)
        self.assertEqual(conf[Program.OPTION_NAME_MAX_RECENT_THREADS], self.FAKE_MAX_RECENT_THREADS)
        self.assertGreater(len(conf[Program.OPTION_NAME_RECENT_THREADS]), 0)

    def test_load_json_dict(self):
        p = Program()
        json_dict = p.load_json_dict(p.config_path())
        self.assertIsNotNone(json_dict)

    def test_load_config(self):
        p = Program()
        json_dict = p.load_json_dict()
        p.set_config(json_dict)
        self.assertEqual(p.DEFAULT_DOWNLOAD_DIR, self.FAKE_DOWNLOAD_DIR)
        self.assertEqual(p.DEFAULT_MAX_RECENT_THREADS, self.FAKE_MAX_RECENT_THREADS)
        self.assertGreater(len(p.recent_threads), 0)

    def test_auto_load_config(self):
        p = Program(load_config=True)
        self.assertEqual(p.DEFAULT_DOWNLOAD_DIR, self.FAKE_DOWNLOAD_DIR)
        self.assertEqual(p.DEFAULT_MAX_RECENT_THREADS, self.FAKE_MAX_RECENT_THREADS)
        self.assertGreater(len(p.recent_threads), 0)


class ProgramExecuteCommandsTestCase(unittest.TestCase):
    ORIGINAL_CONFIG_DIR = Program.CONFIG_DIR
    FAKE_DOWNLOAD_DIR = os.path.join(TMP_DIRECTORY, '1234567890')
    FAKE_MAX_RECENT_THREADS = 20

    def setUp(self):
        self.config_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.thread_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.download_dir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.parser = CLIParser()
        Program.CONFIG_DIR = self.config_dir.name

        # Create config
        conf = dict()
        # conf[Program.OPTION_NAME_RECENT_THREADS] = [self.thread_dir.name for i in range(self.FAKE_MAX_RECENT_THREADS)]
        conf[Program.OPTION_NAME_RECENT_THREADS] = []
        conf[Program.OPTION_NAME_MAX_RECENT_THREADS] = self.FAKE_MAX_RECENT_THREADS
        conf[Program.OPTION_NAME_DOWNLOAD_DIR] = self.download_dir.name
        with open(os.path.join(Program.CONFIG_DIR, Program.CONFIG_NAME), 'w') as f:
            json.dump(conf, f)

        # Create dummy thread
        create_test_environment(self.thread_dir.name)

    # @unittest.skip
    def test_download_url_to_directory_then_added_to_recent(self):
        cli_input = '{} -d {}'.format(STICKY_THREAD_URL, self.thread_dir.name)
        returned = self.parser.parse_str(cli_input)
        p = Program(returned, True)
        self.assertEqual(p.state, p.State.DOWNLOAD_TO_DIRECTORY)
        p.start(download=False)
        self.assertIn(self.thread_dir.name, p.recent_threads)

    def test_synchronise_to_directory_then_added_to_recent(self):
        create_test_environment(self.thread_dir.name, url=STICKY_THREAD_URL)  # Try online

        cli_input = '-sd {}'.format(self.thread_dir.name)
        returned = self.parser.parse_str(cli_input)
        p = Program(returned, True)
        self.assertEqual(p.state, p.State.SYNCHRONISE_DIRECTORY)
        p.start(download=False)
        self.assertIn(self.thread_dir.name, p.recent_threads)

    def test_settings_get_updated_after_download(self):
        create_test_environment(self.thread_dir.name, url=STICKY_THREAD_URL)  # Try online

        cli_input = '-sd {}'.format(self.thread_dir.name)
        returned = self.parser.parse_str(cli_input)
        p = Program(returned, True)
        p.start(download=False)
        p.reload_config()
        self.assertIn(self.thread_dir.name, p.recent_threads)

    def test_settings_get_updated_dead_thread(self):
        """Using local thread file (a dead thread). Dead threads are not added to config."""
        cli_input = '-sd {}'.format(self.thread_dir.name)
        returned = self.parser.parse_str(cli_input)
        p = Program(returned, True)
        p.start(download=False)
        p.reload_config()
        self.assertNotIn(self.thread_dir.name, p.recent_threads)

    def test_download_to_default_dir(self):
        cli_input = '{}'.format(STICKY_THREAD_URL)
        pass


class SynchroniseRecentTestCase(unittest.TestCase):
    pass