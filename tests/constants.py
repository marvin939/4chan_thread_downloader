import utilities

"""TEST CONSTANTS"""
# Modify these when running unit tests, if the thread is dead.

REAL_THREAD_URL = 'http://boards.4chan.org/wg/thread/7027515'
THREAD_URL = 'http://boards.4chan.org/wg/thread/7027515'
THREAD_ID = '7027515'
EXPECTED_THREAD_TITLE = '/wg/ - Minimalistic papes - Wallpapers/General - 4chan'
THREAD_GONE_REASON = 'The thread is either dead, or the site is down...'
TMP_DIRECTORY = './tmp/'
FAKE_THREAD_URL = THREAD_URL + '404'

if not utilities.url_is_accessible(THREAD_URL):
    print('*****The thread is dead! Please replace with a more recent thread url!*****')