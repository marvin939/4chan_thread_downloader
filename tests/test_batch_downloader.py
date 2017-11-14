from utilities import IgnoreFilter
import re
import requests
import glob
from retriever import LinksRetriever, BatchDownloader
import unittest
import os
import utilities
from tests.constants import *


class BatchDownloaderInstantiateTestCase(unittest.TestCase):

    # def test_instantiate_with_non_iterable(self):
    #     with self.assertRaises(TypeError):
    #         downloader = BatchDownloader(123456)

    def test_instantiate_with_link_retriever(self):
        getter = LinksRetriever('test_thread.html')
        downloader = BatchDownloader(getter)
        self.assertEqual(downloader.links_retriever, getter)

    def test_instantiate_with_destination_folder(self):
        getter = LinksRetriever('test_thread.html')
        destination_dir = os.path.expanduser('~/Downloads/')
        downloader = BatchDownloader(getter, destination_dir)
        self.assertEqual(downloader.destination_folder, destination_dir)

    # def test_instantiate_with_many_links_retriever(self):
    #     getters = (LinksRetriever('test_thread.html'), LinksRetriever(requests.get(THREAD_URL)))
    #     destination_dir = os.path.expanduser('~/Downloads/')
    #     downloader = BatchDownloader(getters, destination_dir)
    #     self.assertEqual(downloader.retrievers, getters)


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



# @unittest.skipUnless(utilities.url_is_accessible(THREAD_URL), THREAD_GONE_REASON)
# class ThreadDownloaderDownloadOnceTestCase(unittest.TestCase):

@unittest.skipUnless(utilities.url_is_accessible(THREAD_URL), THREAD_GONE_REASON)
class BatchDownloaderDownloadingTestCase(unittest.TestCase):

    GET_NUM_FILES = 3

    def setUp(self):
        self.linkser = LinksRetriever(THREAD_URL)
        #self.destination_directory = os.path.expanduser('~/Downloads/TestDownloadThread/')
        self.destination_directory = TMP_DIRECTORY
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)
        self.download_files()

    def download_files(self):
        for url in self.linkser.get_all_file_links()[:self.GET_NUM_FILES]:
            download_path = utilities.download_file(url, self.downloader.destination_folder)
            assert os.path.exists(download_path)

    def tearDown(self):
        for url in self.linkser.get_all_file_links()[:self.GET_NUM_FILES]:
            os.remove(os.path.join(self.destination_directory, os.path.basename(url)))

    def test_files_downloaded(self):
        downloaded = self.downloader.get_files_downloaded()
        self.assertEqual(len(downloaded), self.GET_NUM_FILES)

    def test_files_not_downloaded_gen(self):
        not_downloaded = self.downloader.links_not_downloaded()
        self.assertIsNotNone(not_downloaded)
        not_downloaded_tuple = tuple(not_downloaded)
        self.assertEqual(len(not_downloaded_tuple), len(self.downloader.files_to_download) - len(self.downloader.get_files_downloaded()))

    def test_compare_downloaded(self):
        not_downloaded = tuple(self.downloader.get_links_not_downloaded())
        self.assertEqual(len(not_downloaded), len(self.linkser.get_all_file_links()) - self.GET_NUM_FILES)


@unittest.skipUnless(utilities.url_is_accessible(THREAD_URL), THREAD_GONE_REASON)
class BatchDownloaderDetailsTestCase(unittest.TestCase):

    def setUp(self):
        self.linkser = LinksRetriever(THREAD_URL)
        self.destination_directory = os.path.expanduser(TMP_DIRECTORY)
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)
        self.downloader.pickle_details()

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
        loaded = BatchDownloader.load_details_into_dict(self.downloader.get_details_path())
        self.assertTrue(isinstance(loaded, dict))
        self.assertEqual(loaded, details)

    def test_compare_details(self):
        down = BatchDownloader(self.linkser, './tmp/')
        details = down.construct_details_dict()
        down.pickle_details()
        loaded = BatchDownloader.load_details_into_dict(self.downloader.get_details_path())

        self.assertEqual(loaded['last-modified'], details['last-modified'])
        self.assertEqual(loaded['url'], details['url'])
        self.assertEqual(loaded['thread_alive'], details['thread_alive'])

    def test_pickle_details_custom_details(self):
        custom_details = {'last-modified':'123456', 'thread_alive': False, 'url':THREAD_URL}
        down = BatchDownloader(self.linkser, './tmp/')
        #details = down.construct_details_dict()
        down.pickle_details(custom_details)
        loaded = BatchDownloader.load_details_into_dict(self.downloader.get_details_path())

        self.assertEqual(loaded['last-modified'], custom_details['last-modified'])
        self.assertEqual(loaded['url'], custom_details['url'])
        self.assertEqual(loaded['thread_alive'], custom_details['thread_alive'])

    def test_thread_404_but_has_details(self):
        fake_url = THREAD_URL + '404'
        self.linkser = LinksRetriever(fake_url)
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)
        # update the details pickle

        self.assertTrue(self.linkser.thread_is_dead())
        details = BatchDownloader.load_details_into_dict(self.downloader.get_details_path())
        self.assertIsNotNone(details)
        self.assertTrue(details['thread_alive'], True)  # Hasn't been updated yet...

    def test_thread_update_details_pickle_thread_dead(self):
        fake_url = THREAD_URL + '404'
        self.linkser = LinksRetriever(fake_url)
        self.downloader = BatchDownloader(self.linkser, self.destination_directory)
        details = BatchDownloader.load_details_into_dict(self.downloader.get_details_path())
        self.assertIsNotNone(details)

        details['thread_alive'] = False
        self.assertFalse(details['thread_alive'])
        self.downloader.pickle_details(details)

        loaded = BatchDownloader.load_details_into_dict(self.downloader.get_details_path())
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['thread_alive'], details['thread_alive'])


class ThreadDownloaderWithIgnoreFilteringTestCase(unittest.TestCase):

    def setUp(self):
        self.downloader = BatchDownloader(LinksRetriever('test_thread.html'), TMP_DIRECTORY)
        self.downloader.ifilter = IgnoreFilter(SOME_THREAD_FILE_URLS)    # Just a normal one, without regular expressions

    def test_get_links(self):
        all_links = self.downloader.links_retriever.get_all_file_links()
        downloaded = self.downloader.get_files_downloaded()
        ignored = self.downloader.ifilter.filter_list

        file_links = tuple(self.downloader.get_links())  # implied filtered=True (default)
        self.assertEqual(len(file_links), len(all_links) - len(downloaded) - len(ignored))

    def test_get_links_filtered_false(self):
        all_links = self.downloader.links_retriever.get_all_file_links()
        downloaded = self.downloader.get_files_downloaded()
        ignored = self.downloader.ifilter.filter_list

        file_links = self.downloader.get_links(filtered=False)  # do not use ifilter.filter()
        self.assertEqual(len(file_links), len(all_links) - len(downloaded))


class ThreadDownloaderInstantiateFromExistingFolder(unittest.TestCase):
    def setUp(self):
        from tempfile import TemporaryDirectory
        self.links_retriever = None
        self.existing_directory = os.path.join(TMP_DIRECTORY, 'temp_download_dir')
        self.createTestEnvironment(self.existing_directory)

    def createTestEnvironment(self, dirname):
        utilities.create_directory_tree(dirname)

        downloader = BatchDownloader(LinksRetriever('test_thread.html'), dirname)
        downloader.pickle_details()
        ifilter = IgnoreFilter(['\w+\.png'], is_regex=True)
        ifilter.save(os.path.join(dirname, downloader.IGNORE_LIST_FILENAME))
        # pass

    def test_instantiate_from_existing_folder(self):
        """Downloader can instantiate self from an existing folder if that folder has a thread_details.pkl file that it can load,
        and optionally, an ignore list text file, or a few already downloaded files. As long as the thread_details.pkl
        file exists, it is ok to instantiate one from a directory."""
        downloader = BatchDownloader.from_directory(self.existing_directory)
        self.assertIsNotNone(downloader)
        self.assertIsNotNone(downloader.links_retriever)