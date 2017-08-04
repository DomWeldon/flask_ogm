import json
from unittest import TestCase

from examples.simple_app import app

"""
ALL TESTS HEREIN RELY ON THE SMALL MOVIE GRAPH BEING ACCESSIBLE IN A
GRAPH ON LOCALHOST.
"""


class MovieAppTestCase(TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_count_movies(self):
        with self.app.app_context():
            r = self.app.test_client().get('/')
            i = int(r.get_data(as_text=True))
            assert i > 0
