import unittest
import utilities
import os
import shutil


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