from retriever import LinksRetriever
import unittest
import re


class LinksRetrieverTitleRegexTestCase(unittest.TestCase):

    EXAMPLE_TITLE = '       /g/ - Waiting for Ryzen thread - Technology - 4chan'
    EXPECTED_THREAD_BOARD_NAME = 'g'
    EXPECTED_THREAD_TITLE = 'Waiting for Ryzen thread'

    def test_match_title(self):
        matches = LinksRetriever.RE_TITLE.search(self.EXAMPLE_TITLE)
        self.assertIsNotNone(matches)

    def test_group_match_title_board(self):
        matches = LinksRetriever.RE_TITLE.search(self.EXAMPLE_TITLE)
        self.assertEqual(matches('board'), self.EXPECTED_THREAD_BOARD_NAME)

    def test_group_match_thread_title(self):
        matches = LinksRetriever.RE_TITLE.search(self.EXAMPLE_TITLE)
        self.assertEqual(matches('title'), self.EXPECTED_THREAD_TITLE)


'''Tests for other compiled regex patterns'''
