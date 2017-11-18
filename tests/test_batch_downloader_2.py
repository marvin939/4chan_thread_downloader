from tests.constants import *
from retriever import LinksRetriever, BatchDownloader
import unittest


class BatchDownloaderGenerateDirectoryPath(unittest.TestCase):

    def setUp(self):
        BatchDownloader.DEBUG = True

    # def test_no_destination_folder(self):
    #     links_retriever = LinksRetriever(TEST_THREAD_FILENAME)
    #     downloader = BatchDownloader(links_retriever, None)
    #
    #     expected_directory
    #     self.assertTrue()