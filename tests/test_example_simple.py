from unittest import TestCase

from examples.simple_app import app

"""For example, the below is equivalent to :ref:`quick_start_with_primary_key`
ALL TESTS HEREIN RELY ON THE SMALL MOVIE GRAPH BEING ACCESSIBLE IN A
GRAPH ON LOCALHOST.
"""


class SimpleAppTestCase(TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_count_movies(self):
        with self.app.app_context():
            r = self.app.test_client().get('/')
            i = int(r.get_data(as_text=True))
            assert i > 0
