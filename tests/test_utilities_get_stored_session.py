import thread_files.utilities as utilities
import unittest


class GetStoredSessionTestCase(unittest.TestCase):

    def test_get_session(self):
        session = utilities.get_stored_session()
        self.assertIsNotNone(session)

    def test_check_global_stored(self):
        """Check if the __STORED_SESSION variable is actually stored, using two instances of its getter"""
        session = utilities.get_stored_session()
        session2 = utilities.get_stored_session()
        self.assertEqual(session, session2)
