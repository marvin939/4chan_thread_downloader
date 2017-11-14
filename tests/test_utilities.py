import unittest
import utilities
import os
import shutil
from retriever import *
from tests.constants import *
from utilities import IgnoreFilter
from tempfile import TemporaryDirectory


class UrlIsAccessibleTestCase(unittest.TestCase):
    VALID_URL = 'http://google.com'
    NON_EXIST_URL = 'http://fsakjfasddfhuioy.com'

    def test_try_access_valid(self):
        self.assertTrue(utilities.url_is_accessible(self.VALID_URL))

    def test_try_access_invalid(self):
        self.assertFalse(utilities.url_is_accessible(self.NON_EXIST_URL))


class UrlRetrievalTestCase(unittest.TestCase):
    TEST_URL = 'http://www.google.com'

    # def setUp(self):
    #     self.soup = BeautifulSoup(self.urlr())

    def test_retrieve_not_none(self):
        retrieved = utilities.retrieve_url_as_string(self.TEST_URL)
        self.assertIsNotNone(retrieved)

    def test_retrieve_contents_text(self):
        retrieved = utilities.retrieve_url_as_string(self.TEST_URL)
        self.assertIn('Google', 'Google')


class DownloadUrlTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = os.path.expanduser('~/Downloads/')
        self.filename = 'banner123.png'
        self.destination = os.path.join(self.directory, self.filename)
        self.url = 'http://s.4cdn.org/image/title/167.png'
        self.tearDown()

    def test_download_to_directory_without_filename(self):
        downloaded_path = utilities.download_file(self.url, directory=self.directory)
        self.assertTrue(os.path.exists(downloaded_path))
        expected_path = os.path.abspath(os.path.join(self.directory, os.path.basename(self.url)))
        self.assertEqual(downloaded_path, expected_path)

    def test_download_to_current_working_directory_without_filename(self):
        filename = os.path.basename(self.url)
        expected_destination = os.path.join(os.getcwd(), filename)
        downloaded_path = utilities.download_file(self.url)

        self.assertTrue(os.path.exists(downloaded_path))
        self.assertEqual(expected_destination, downloaded_path)

    def test_download_with_filename_and_directory(self):
        expected_destination = utilities.download_file(self.url, self.directory, self.filename)
        self.assertEqual(expected_destination, os.path.join(self.directory, self.filename))
        self.assertEqual(os.path.basename(expected_destination), self.filename)
        # print(expected_destination)

    def tearDown(self):
        if os.path.exists(self.destination):
            try:
                os.remove(self.destination)
            except IsADirectoryError:
                shutil.rmtree(self.destination)
        if os.path.exists(self.filename):
            os.remove(self.filename)


class DownloadUrlOverrideFileTestCase(unittest.TestCase):
    def setUp(self):
        self.url = 'https://www.python.org/static/img/python-logo.png'
        self.tempdir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.download_directory = self.tempdir.name
        utilities.download_file(self.url, self.download_directory)  # Save it now
        print('temporary directory:', self.download_directory)

    def test_download_with_overwrite_false(self):
        with self.assertRaises(FileExistsError):
            utilities.download_file(self.url, self.download_directory, overwrite=False)

    def test_download_with_overwrite_enabled(self):
        save_path = utilities.download_file(self.url, self.download_directory, overwrite=True)
        self.assertTrue(os.path.exists(save_path))


class IgnoreFilterSaveLoadTestCase(unittest.TestCase):
    def setUp(self):
        self.ignore_list_path = os.path.join(TMP_DIRECTORY, BatchDownloader.IGNORE_LIST_FILENAME)
        self.ignore_list_contents = SOME_THREAD_FILE_URLS
        self.create_ignore_list_file(self.ignore_list_contents)
        self.fake_path = self.ignore_list_path + '123'

    def create_ignore_list_file(self, ignore_list_contents):
        with open(self.ignore_list_path, 'w') as fh:
            fh.write('\n'.join(ignore_list_contents))

    def tearDown(self):
        if os.path.exists(self.ignore_list_path):
            os.remove(self.ignore_list_path)
        if os.path.exists(self.fake_path):
            os.remove(self.fake_path)

    def test_load_filter_list_regex(self):
        fil = IgnoreFilter.load_filter(self.ignore_list_path)
        # self.assertEqual(fil.filter_list, self.ignore_list_contents)
        self.assertIsNotNone(fil)
        self.assertIsNotNone(fil.filter_list)
        self.assertTrue(not isinstance(fil.filter_list[0], str))

    def test_source_path(self):
        fil = IgnoreFilter.load_filter(self.ignore_list_path)
        self.assertEqual(fil.source_path, self.ignore_list_path)
        self.assertTrue(os.path.exists(fil.source_path))

    def test_save_filter_list_custom_path(self):
        fil = IgnoreFilter.load_filter(self.ignore_list_path)
        fil.save(self.fake_path) # Custom path
        self.assertTrue(os.path.exists(self.fake_path))

    def test_save_filter_list_default_path(self):
        fil = IgnoreFilter.load_filter(self.ignore_list_path)
        os.remove(self.ignore_list_path)
        fil.save()  # No path
        self.assertTrue(os.path.exists(self.ignore_list_path))

    def test_save_filter_list_no_source_path_error_raised(self):
        fil = IgnoreFilter.load_filter(self.ignore_list_path)
        fil.source_path = None
        with self.assertRaises(ValueError):
            fil.save()

    def test_save_filter_list_no_source_path_error_raised_and_not_saved(self):
        fil = IgnoreFilter.load_filter(self.ignore_list_path)
        fil.source_path = None
        os.remove(self.ignore_list_path)
        with self.assertRaises(ValueError):
            fil.save()
        self.assertFalse(os.path.exists(self.ignore_list_path))


class IgnoreFilterFilteringListsTestCase(unittest.TestCase):
    def setUp(self):
        self.ignore_list_contents = SOME_THREAD_FILE_URLS
        self.fil = IgnoreFilter(self.ignore_list_contents)
        self.png_regex = r'\w+\.png'

    def test_filter_with_ignore_list_containing_regexp(self):
        ignore_list = self.ignore_list_contents + [self.png_regex]
        # ignore_list = self.fil.load_filter(self.ignore_list_path)
        regexp_ignore_list = self.fil.convert_filter_list_to_regex_list(ignore_list)
        for i in range(len(regexp_ignore_list)):
            with self.subTest(i=i):
                self.assertTrue(not isinstance(regexp_ignore_list[i], str))

    def test_regexp_filter_list(self):
        ignore_list = self.ignore_list_contents + [self.png_regex]
        regexp_ignore_list = self.fil.convert_filter_list_to_regex_list(ignore_list)

        test_list = ['123456.png', '123456.jpg', '6789.png']
        result = tuple(self.fil.filter_with_regexp_list(test_list, regexp_ignore_list))
        self.assertEqual(len(result), 1)

    def test_filter_with_ignore_list(self):
        # ignore_list = ['http://i.4cdn.org/wg/1507921740712.jpg', 'https://i.4cdn.org/wg/1506628360792.png']
        downloader = BatchDownloader(LinksRetriever('test_thread.html'))
        not_downloaded = list(downloader.get_links_not_downloaded())
        filtered = list(IgnoreFilter.filter_with_ignore_list(not_downloaded, self.ignore_list_contents))
        self.assertNotIn(self.ignore_list_contents, filtered)
        self.assertEqual(len(filtered), len(not_downloaded) - len(self.ignore_list_contents))

    def test_instantiate_with_normal_list(self):
        fil = IgnoreFilter(self.ignore_list_contents, is_regex=False)
        self.assertEqual(fil.filter_list, self.ignore_list_contents)

    def test_normal_list_filter_function(self):
        """Test that the filter method is the normal one"""
        fil = IgnoreFilter(self.ignore_list_contents, is_regex=False)
        downloader = BatchDownloader(LinksRetriever('test_thread.html'))
        not_downloaded = list(downloader.get_links_not_downloaded())

        filtered = tuple(fil.filter(not_downloaded))
        self.assertNotIn(self.ignore_list_contents, filtered)

    def test_instantiate_with_regex_list(self):
        fil = IgnoreFilter(self.ignore_list_contents, is_regex=True)
        self.assertNotEqual(fil.filter_list, self.ignore_list_contents)

    def test_regex_list_filter_function_no_regex(self):
        fil = IgnoreFilter(self.ignore_list_contents, is_regex=True)
        downloader = BatchDownloader(LinksRetriever('test_thread.html'))
        not_downloaded = list(downloader.get_links_not_downloaded())

        filtered = tuple(fil.filter(not_downloaded))
        # self.assertNotIn(self.ignore_list_contents, filtered)
        for ignore in self.ignore_list_contents:
            self.assertNotIn(ignore, filtered)

    def test_regex_list_filter_function_with_regex(self):
        fil = IgnoreFilter(self.ignore_list_contents + [self.png_regex], is_regex=True)
        test_list = ['123456.png', '123456.jpg', '6789.png']    # only 1 jpg; 2 pngs
        filtered = tuple(fil.filter(test_list))
        self.assertEqual(len(filtered), 1)
