import unittest

from thread_files.retriever import LinksRetriever


class LinksRetrieverTitleRegexTestCase(unittest.TestCase):

    EXAMPLE_TITLE = '       /g/ - Waiting for Ryzen thread - Technology - 4chan'
    EXPECTED_THREAD_BOARD_NAME = 'g'
    EXPECTED_THREAD_TITLE = 'Waiting for Ryzen thread'

    def test_match_title(self):
        matches = LinksRetriever.RE_TITLE.search(self.EXAMPLE_TITLE)
        self.assertIsNotNone(matches)

    def test_group_match_title_board(self):
        matches = LinksRetriever.RE_TITLE.search(self.EXAMPLE_TITLE)
        self.assertEqual(matches.group('board'), self.EXPECTED_THREAD_BOARD_NAME)

    def test_group_match_thread_title(self):
        matches = LinksRetriever.RE_TITLE.search(self.EXAMPLE_TITLE)
        self.assertEqual(matches.group('title'), self.EXPECTED_THREAD_TITLE)


class FourChanUrlRegexTestCase(unittest.TestCase):

    EXAMPLE_URL = 'http://boards.4chan.org/g/thread/60887612'
    EXPECTED_THREAD_BOARD_NAME = 'g'
    EXPECTED_THREAD_THREAD_ID = '60887612'

    def test_match_url(self):
        match = LinksRetriever.RE_FOURCHAN_URL.search(self.EXAMPLE_URL)
        self.assertIsNotNone(match)

    def test_group_match_board(self):
        match = LinksRetriever.RE_FOURCHAN_URL.search(self.EXAMPLE_URL)
        self.assertEqual(match.group('board'), self.EXPECTED_THREAD_BOARD_NAME)

    def test_group_match_thread_id(self):
        match = LinksRetriever.RE_FOURCHAN_URL.search(self.EXAMPLE_URL)
        self.assertEqual(match.group('thread_id'), self.EXPECTED_THREAD_THREAD_ID)


'''Tests for other compiled regex patterns'''
