from tempfile import TemporaryDirectory
import unittest
from retriever import *
import unittest
from tempfile import TemporaryDirectory
from tests.constants import *
from tests.useful import *
from retriever import *

print('THIS WILL TAKE A WHILE SINCE THIS TEST WILL HAVE TO DOWNLOAD EVERYTHING FROM THE THREAD!')


class DownloadTestCase(unittest.TestCase):
    """Downloads from STICKY_THREAD_URL since that usually contains the least images,
    and lasts forever (eg. since 247 days from now)..."""

    def setUp(self):
        self.tempdir = TemporaryDirectory(dir=TMP_DIRECTORY)
        self.tempdir_path = self.tempdir.name
        # self.tempdir_path = os.path.join(TMP_DIRECTORY, 'temp_files')
        print('tempdir_path:', os.path.abspath(self.tempdir_path))
        utilities.create_directory_tree(self.tempdir_path)
        self.downloader = BatchDownloader(LinksRetriever(STICKY_THREAD_URL), self.tempdir_path)

    # def tearDown(self):
    #     utilities.delete_directory_tree(self.tempdir_path)

    def test_download_all(self):
        file_urls = tuple(self.downloader.get_links())
        downloaded = self.downloader.get_files_downloaded()
        self.downloader.start_download()
        after_download = tuple(self.downloader.get_files_downloaded())

        self.assertEqual(len(after_download), len(file_urls) + len(downloaded))
        self.assertEqual(len(self.downloader.get_links()), 0)   # None since all have been downloaded

    # @unittest.expectedFailure
    def test_download_all_also_saves_pickle(self):
        self.downloader.start_download()
        self.assertTrue(os.path.exists(self.downloader.get_details_path()))


class FromExistingDirectoryDownloadFromDeadThreadTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = TemporaryDirectory(dir=TMP_DIRECTORY)
        create_test_environment(self.tempdir.name, 3, url=STICKY_THREAD_URL)
        self.downloader = BatchDownloader.from_directory(self.tempdir.name)

    def test_download_all_pickle_thread_alive_updated(self):
        # Don't need to write a test... this has already been tested in test_links_retriever.py's thread_alive function.
        # The thread_alive function already returns boolean based on whether the current thread is alive or not.
        pass
