from py2neo import Graph

from .util import Flask, FlaskOGMTestCase
from flask_ogm import OGM

class TestTestCase(FlaskOGMTestCase):
    def test_create_test_app(self):
        app, client = self.create_test_app(SOME_PARAM = 'value')
        assert isinstance(app, Flask)
        assert'SOME_PARAM' in app.config and app.config['SOME_PARAM'] == 'value'

    def test_factory_method_creation(self):
        app, client = self.create_test_app(
            OGM_GRAPH_HOST = 'localhost',
            OGM_GRAPH_USER = 'neo4j',
            OGM_GRAPH_PASSWORD = 'password',
            OGM_GRAPH_PROTOCOL = 'http',
            OGM_GRAPH_PORT = '7474'
        )
        ogm = OGM()
        with app.app_context():
            ogm.init_app(app)
            assert isinstance(ogm.graph, Graph)
