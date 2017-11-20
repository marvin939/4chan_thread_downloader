import os
from tempfile import TemporaryDirectory
from thread_files import utilities

"""VOLATILE TEST CONSTANTS"""
# Modify these when running unit tests, if the thread is dead.
STICKY_THREAD_URL = 'http://boards.4chan.org/wg/thread/6872254'
THREAD_URL = 'http://boards.4chan.org/wg/thread/7027515'
REAL_THREAD_URL = THREAD_URL
EXPECTED_BOARD_INITIALS = 'wg'
EXPECTED_THREAD_ID = '7027515'
EXPECTED_THREAD_HTML_TITLE = '/wg/ - Minimalistic papes - Wallpapers/General - 4chan'
SOME_THREAD_FILE_URLS = ['http://i.4cdn.org/wg/1507921740712.jpg', 'https://i.4cdn.org/wg/1506628360792.png']


"""NON-VOLATILE TEST CONSTANTS (Testing constants that rarely change)"""
THREAD_GONE_REASON = 'The thread is either dead, or the site is down...'
TMP_DIRECTORY = './tmp/'
FAKE_THREAD_URL = THREAD_URL + '404'
# TEST_THREAD_FILENAME = 'tests/test_thread.html'
TEST_THREAD_FILENAME = 'test_thread.html'


"""OVERRIDES WHEN TESTING"""
utilities.CACHE_DIR = '.web_cache'
utilities.DBG_CACHED_DOWNLOAD = True


if not utilities.url_is_accessible(THREAD_URL):
    raise ValueError(
        '*****The thread is dead! Please replace with a more recent thread URL!*****\n'
        '*****Remember to change the other constants too!*****')

if not utilities.url_is_accessible(STICKY_THREAD_URL):
    raise ValueError(
        '*****The sticky thread is dead! Please replace with a more recent thread URL!*****\n'
        '*****Remember to change the other constants too!*****')