from tempfile import TemporaryDirectory
from tests.constants import *
import unittest
from retriever import *


print('THIS WILL TAKE A WHILE SINCE THIS TEST WILL HAVE TO DOWNLOAD EVERYTHING FROM THE THREAD!')

class DownloadTestCase(unittest.TestCase):

    def setUp(self):
        # self.tempdir = TemporaryDirectory(dir=TMP_DIRECTORY)
        # self.tempdir_path = self.tempdir.name
        self.tempdir_path = os.path.join(TMP_DIRECTORY, 'temp_files')
        print('tempdir:', self.tempdir_path)
        utilities.create_directory_tree(self.tempdir_path)
        self.downloader = BatchDownloader(LinksRetriever(STICKY_THREAD_URL), self.tempdir_path)

    def test_download_all(self):
        file_urls = tuple(self.downloader.get_links())
        downloaded = self.downloader.get_files_downloaded()
        self.downloader.start_download()
        after_download = tuple(self.downloader.get_files_downloaded())

        self.assertEqual(len(after_download), len(file_urls) + len(downloaded))
        self.assertEqual(len(self.downloader.get_links()), 0)   # None since all have been downloaded

