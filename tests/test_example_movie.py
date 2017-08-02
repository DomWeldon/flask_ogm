import json
from unittest import TestCase
from werkzeug.exceptions import NotFound

from flask_ogm import OGM

from examples.movie_app import app, ogm

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
            r = self.app.test_client().get('/count/movies')
            d = json.loads(r.get_data(as_text=True))
            assert d == {
                'primary_label': 'Movie',
                'total': 38
            }
    def test_count_people(self):
        with self.app.app_context():
            r = self.app.test_client().get('/count/people')
            d = json.loads(r.get_data(as_text=True))
            assert d == {
                'primary_label': 'Person',
                'total': 131
            }

    def test_get_movie(self):
        with self.app.app_context():
            r = self.app.test_client().get('/movie/The Matrix')
            d = json.loads(r.get_data(as_text=True))
            assert len(d['producers']) == 1
            assert len(d['actors']) == 5
            assert len(d['directors']) == 2
            assert d['movie'] == {
                'released': 1999,
                'title': 'The Matrix',
                'tag_line': 'Welcome to the Real World'
            }

    def test_get_person(self):
        with self.app.app_context():
            r = self.app.test_client().get('/person/Tom Hanks')
            d = json.loads(r.get_data(as_text=True))
            assert len(d['acted_in']) == 12
            assert len(d['directed']) == 1
            assert len(d['produced']) == 0
            assert d['person'] == {
                'name': 'Tom Hanks',
                'born': 1956,
            }

    def test_get_person2(self):
        with self.app.app_context():
            r = self.app.test_client().get('/person/Lilly Wachowski')
            d = json.loads(r.get_data(as_text=True))
            assert len(d['directed']) == 5
            assert len(d['produced']) == 2
            assert d['person'] == {
                'name': 'Lilly Wachowski',
                'born': 1967,
            }

    def test_not_found(self):
        """If this test fails, call the Daily Mail"""
        with self.app.app_context():
            r = self.app.test_client().get('/person/Lord Lucan')
            assert r.status == '404 NOT FOUND'

    def test_films_by_year(self):
        with self.app.app_context():
            r = self.app.test_client().get('/movies/by/year/2004')
            d = json.loads(r.get_data(as_text=True))
            assert len(d) == 1
