import glob
from retriever import LinksRetriever, BatchDownloader
import unittest
import os
import utilities
from tests.constants import *


class BatchDownloaderInstantiateTestCase(unittest.TestCase):

    def test_instantiate_with_url_list(self):
        downloader = BatchDownloader(['abcdef.png', '123456.jpg'])
        '''Fix this test'''

    def test_instantiate_with_non_iterable(self):
        with self.assertRaises(TypeError):
            downloader = BatchDownloader(123456)

    def test_instantiate_with_link_retriever(self):
        getter = LinksRetriever('test_thread.html')
        downloader = BatchDownloader(getter)
        self.assertEqual(downloader.links_retriever, getter)

    def test_instantiate_with_destination_folder(self):
        getter = LinksRetriever('test_thread.html')
        destination_dir = os.path.expanduser('~/Downloads/')
        downloader = BatchDownloader(getter, destination_dir)
        self.assertEqual(downloader.destination_folder, destination_dir)

    '''Class should also deal with differences between downloaded files and files to be downloaded'''


class BatchDownloaderTestCase(unittest.TestCase):
    # pass

    def setUp(self):
        self.linkser = LinksRetriever(REAL_THREAD_URL)
        self.destination_directory = os.path.expanduser('~/Downloads/TestDownloadThread/')
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)

        #self.thread_download_directory = os.path.join(self.destination_directory, BatchDownloader.THREAD_SAVE_NAME)

    def tearDown(self):
        # Delete all downloaded files
        utilities.delete_directory_tree(self.destination_directory)

    def test_files_to_download(self):
        pass
        '''
        In unit tests, downloaded shouldn't really download. 
        Instead, it should just present a list of things to be downloaded, 
        or the paths of the files that have been downloaded.
        '''

    def test_download_html(self):
        self.downloader.save_html()  # Downloads the HTML to the destination
        self.assertTrue(os.path.exists(os.path.join(self.destination_directory, BatchDownloader.THREAD_SAVE_NAME)))

    def test_pickle_details_save_exists(self):
        self.downloader.pickle_details()
        self.assertTrue(os.path.exists(os.path.join(self.destination_directory, BatchDownloader.THREAD_DETAILS_FILENAME)))

    def test_construct_details_dict(self):
        details = self.downloader.construct_details_dict()
        keys = details.keys()
        self.assertIn('last-modified', keys)
        self.assertTrue(isinstance(details['last-modified'], str))
        self.assertIn('url', keys)
        self.assertTrue(isinstance(details['url'], str))
        self.assertIn('thread_alive', keys)
        self.assertTrue(isinstance(details['thread_alive'], bool))

    def test_load_details(self):
        down = BatchDownloader(self.linkser, './tmp/')
        details = down.construct_details_dict()
        down.pickle_details()
        loaded = down.load_details_into_dict()
        self.assertTrue(isinstance(loaded, dict))
        self.assertEqual(loaded, details)

    def test_compare_details(self):
        down = BatchDownloader(self.linkser, './tmp/')
        details = down.construct_details_dict()
        down.pickle_details()
        loaded = down.load_details_into_dict()

        self.assertEqual(loaded['last-modified'], details['last-modified'])
        self.assertEqual(loaded['url'], details['url'])
        self.assertEqual(loaded['thread_alive'], details['thread_alive'])

    def test_pickle_details_custom_details(self):
        custom_details = {'last-modified':'123456', 'thread_alive': False, 'url':THREAD_URL}
        down = BatchDownloader(self.linkser, './tmp/')
        #details = down.construct_details_dict()
        down.pickle_details(custom_details)
        loaded = down.load_details_into_dict()

        self.assertEqual(loaded['last-modified'], custom_details['last-modified'])
        self.assertEqual(loaded['url'], custom_details['url'])
        self.assertEqual(loaded['thread_alive'], custom_details['thread_alive'])


class BatchDownloaderDownloadingTestCase(unittest.TestCase):

    GET_NUM_FILES = 3

    def setUp(self):
        self.linkser = LinksRetriever(REAL_THREAD_URL)
        #self.destination_directory = os.path.expanduser('~/Downloads/TestDownloadThread/')
        self.destination_directory = TMP_DIRECTORY
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)

    def test_download_files(self):
        # Get first 3 files
        for url in self.linkser.get_all_file_links()[:self.GET_NUM_FILES]:
            download_path = utilities.download_file(url, self.downloader.destination_folder)
            self.assertTrue(os.path.exists(download_path))

    def test_files_downloaded(self):
        downloaded = self.downloader.get_files_downloaded()
        self.assertEqual(len(downloaded), self.GET_NUM_FILES)

    def test_compare_downloaded(self):
        not_downloaded = tuple(self.downloader.get_links_not_downloaded())
        self.assertEqual(len(not_downloaded), len(self.linkser.get_all_file_links()) - self.GET_NUM_FILES)

    def test_download_exceptions(self):
        pass


class BatchDownloaderDetailsTestCase(unittest.TestCase):

    def setUp(self):
        self.linkser = LinksRetriever(REAL_THREAD_URL)
        self.destination_directory = os.path.expanduser(TMP_DIRECTORY)
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)
        self.downloader.pickle_details()

    def test_thread_404_but_has_details(self):
        fake_url = THREAD_URL + '404'
        self.linkser = LinksRetriever(fake_url)
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)
        # update the details pickle

        self.assertTrue(self.linkser.thread_is_dead())
        details = self.downloader.load_details_into_dict()
        self.assertIsNotNone(details)
        self.assertTrue(details['thread_alive'], True)  # Hasn't been updated yet...

    def test_thread_update_details_pickle_thread_dead(self):
        fake_url = THREAD_URL + '404'
        self.linkser = LinksRetriever(fake_url)
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)
        details = self.downloader.load_details_into_dict()
        self.assertIsNotNone(details)

        details['thread_alive'] = False
        self.assertFalse(details['thread_alive'])
        self.downloader.pickle_details(details)

        loaded = self.downloader.load_details_into_dict()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['thread_alive'], details['thread_alive'])