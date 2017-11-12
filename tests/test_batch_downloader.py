from retriever import LinksRetriever, BatchDownloader
import unittest
import os
import utilities


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
        self.linkser = LinksRetriever('http://boards.4chan.org/wg/thread/7027515')
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
