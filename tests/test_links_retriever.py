import unittest

import utilities
from retriever import *
from tests.constants import *


class LinksRetrieverInstantiateTestCase(unittest.TestCase):

    def test_create_instance_from_hdd(self):
        expected_title = '/wg/ - Minimalistic papes - Wallpapers/General - 4chan'
        linkser = LinksRetriever('test_thread.html')  # It's in hdd
        self.assertIsNotNone(linkser.soup)
        self.assertEqual(linkser.soup.title.text, expected_title)

    @unittest.skipUnless(utilities.url_is_accessible(THREAD_URL), THREAD_GONE_REASON)
    def test_create_instance_from_url(self):
        linkser = LinksRetriever(THREAD_URL)
        self.assertIsNotNone(linkser.soup)
        self.assertEqual(linkser.soup.title.text, EXPECTED_THREAD_TITLE)

    @unittest.skipUnless(utilities.url_is_accessible(THREAD_URL), THREAD_GONE_REASON)
    def test_create_instance_from_requests_response(self):
        linkser = LinksRetriever(requests.get(THREAD_URL))
        self.assertIsNotNone(linkser.soup)
        self.assertEqual(linkser.soup.title.text, EXPECTED_THREAD_TITLE)

    @unittest.skipUnless(utilities.url_is_accessible(THREAD_URL), THREAD_GONE_REASON)
    def test_response_saved_if_requests_used(self):
        linkser = LinksRetriever(requests.get(THREAD_URL))
        self.assertIsNotNone(linkser.response)

    @unittest.skipUnless(utilities.url_is_accessible(THREAD_URL), THREAD_GONE_REASON)
    def test_response_saved_if_url_used(self):
        linkser = LinksRetriever(THREAD_URL)
        self.assertIsNotNone(linkser.response)

    def test_instantiating_with_unsupported_url_type(self):
        with self.assertRaises(TypeError):
            linkser = LinksRetriever(123456)

    def test_instantiating_with_non_existent_thread_file(self):
        with self.assertRaises(FileNotFoundError):
            LinksRetriever('iauygiuoasdfyyiorwe')
        with self.assertRaises(FileNotFoundError):
            LinksRetriever('iauygiuoasdfyyiorwe.html')


class LinksRetrieverFromHDDTestCase(unittest.TestCase):

    def setUp(self):
        self.retriever = LinksRetriever('test_thread.html')

    def test_get_thread_id(self):
        id = self.retriever.thread_id
        self.assertEqual(id, "")
        # None since retrieving from hdd

    def test_get_title(self):
        self.assertIn(self.retriever.title, EXPECTED_THREAD_TITLE)
        # title property retrieves thread title without the id and board details

    def test_retrieve_all_file_links(self):
        first_file = 'https://i.4cdn.org/wg/1506493484747.png'
        last_file = 'https://i.4cdn.org/wg/1510456460475.png'
        links = self.retriever.get_all_file_links()
        self.assertIn(first_file, links)
        self.assertIn(last_file, links)

    def test_from_hdd(self):
        self.assertTrue(self.retriever.from_hdd)

    def test_thread_dead_when_from_hdd(self):
        self.assertTrue(self.retriever.thread_is_dead())

    def test_get_html(self):
        self.assertIsNotNone(self.retriever.get_html())


class LinksRetrieverFromOnlineTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_url = THREAD_URL + '404'  # simulate dead thread
        self.retriever = LinksRetriever(self.fake_url)

    def test_thread_is_dead(self):
        self.assertTrue(self.retriever.thread_is_dead())

    def test_thread_is_alive(self):
        self.retriever = LinksRetriever(THREAD_URL)
        self.assertFalse(self.retriever.thread_is_dead())

    def test_get_html(self):
        self.assertIsNotNone(self.retriever.get_html())


class UrlDownloaderTestCase(unittest.TestCase):
    pass