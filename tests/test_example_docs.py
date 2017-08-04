import json
from unittest import TestCase
from werkzeug.exceptions import ImATeapot

from examples.docs_app import app, custom_not_found_callable
from .fixtures import Widget

"""
ALL TESTS HEREIN RELY ON THE SMALL MOVIE GRAPH BEING ACCESSIBLE IN A
GRAPH ON LOCALHOST.
"""


class DocsAppTestCase(TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_get_widget_by_id(self):
        with self.app.app_context():
            r = self.app.test_client().get('/widget_by_id/1')
            d = json.loads(r.get_data(as_text=True))
            assert d['widget'] == Widget.MOCK_DATA[0]

    def test_get_widget_by_name(self):
        with self.app.app_context():
            r = self.app.test_client().get('/widget_by_name/Widget 1')
            d = json.loads(r.get_data(as_text=True))
            assert d['widget'] == Widget.MOCK_DATA[0]

    def test_get_widget_by_id2(self):
        with self.app.app_context():
            r = self.app.test_client().get('/widget_by_id/1')
            d = json.loads(r.get_data(as_text=True))
            assert d['widget'] == Widget.MOCK_DATA[0]

    def test_get_widget_by_composite_id(self):
        with self.app.app_context():
            r = self.app.test_client().get('/widget_by_composite_id/widget:1')
            d = json.loads(r.get_data(as_text=True))
            assert d['widget'] == Widget.MOCK_DATA[0]

    def test_get_widgets_by_colour(self):
        with self.app.app_context():
            r = self.app.test_client().get('/widgets_by_colour/red')
            d = json.loads(r.get_data(as_text=True))
            assert len(d['widgets']) == 2

    def test_not_found_specify_custom_callable(self):
        with self.app.app_context():
            r = self.app.test_client().get('/widget_by_id4/4')
            s = r.get_data(as_text=True)
            assert s == custom_not_found_callable()

    def test_not_found_specify_string(self):
        with self.app.app_context():
            r = self.app.test_client().get('/widget_by_id5/4')
            s = r.get_data(as_text=True)
            assert s == 'Sorry, no widget found!'

    def test_not_found_specify_http_status(self):
        with self.app.app_context():
            r = self.app.test_client().get('/widget_by_id6/4')
            assert r.status == '418 I\'M A TEAPOT'

    def test_check_unique_pass(self):
        with self.app.app_context():
            r = self.app.test_client().get('/only_widget_with_colour/blue')
            assert r.status == '200 OK'

    def test_check_unique_fail(self):
        with self.app.app_context():
            r = self.app.test_client().get('/only_widget_with_colour/red')
            assert r.status == '500 INTERNAL SERVER ERROR'


    def test_search_widgets_by_name(self):
        with self.app.app_context():
            r = self.app.test_client().get('/search_widgets_by_name/Wid')
            d = json.loads(r.get_data(as_text=True))
            assert len(d['widgets']) == 3
            assert d['search_term'] == 'Wid'
