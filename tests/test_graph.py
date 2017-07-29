from py2neo import Graph

from . import *
from .util import FlaskOGMTestCase

class GraphTestCase(FlaskOGMTestCase):
    def test_default_connection_simple_no_optional_params(self):
        app, client = self.create_test_app(
            OGM_GRAPH_HOST = 'localhost',
            OGM_GRAPH_USER = 'neo4j',
            OGM_GRAPH_PASSWORD = 'password'
        )
        with app.app_context():
            ogm = OGM(app)
            assert isinstance(ogm.graph, Graph)

    def test_default_connection_simple_all_params(self):
        app, client = self.create_test_app(
            OGM_GRAPH_HOST = 'localhost',
            OGM_GRAPH_USER = 'neo4j',
            OGM_GRAPH_PASSWORD = 'password',
            OGM_GRAPH_PORT = '7687',
            OGM_GRAPH_PROTOCOL = 'bolt'
        )
        with app.app_context():
            ogm = OGM(app)
            assert isinstance(ogm.graph, Graph)

    def test_default_connection_bound_no_optional_params(self):
        app, client = self.create_test_app(
            OGM_GRAPH_CREDENTIALS = {
                'DEFAULT': dict(
                    HOST = 'localhost',
                    USER = 'neo4j',
                    PASSWORD = 'password'),
            }
        )
        with app.app_context():
            ogm = OGM(app)
            assert isinstance(ogm.graph, Graph)

    def test_default_connection_bound_all_params(self):
        app, client = self.create_test_app(
            OGM_GRAPH_CREDENTIALS = {
                'DEFAULT': dict(
                    HOST = 'localhost',
                    USER = 'neo4j',
                    PASSWORD = 'password',
                    PORT = '7687',
                    PROTOCOL = 'bolt'),
            }
        )
        with app.app_context():
            ogm = OGM(app)
            assert isinstance(ogm.graph, Graph)

    def test_bound_connection_no_optional_params(self):
        app, client = self.create_test_app(
            OGM_GRAPH_CREDENTIALS = {
                'SOME_CONN': dict(
                    HOST = 'localhost',
                    USER = 'neo4j',
                    PASSWORD = 'password'),
            }
        )
        with app.app_context():
            ogm = OGM(app)
            assert isinstance(ogm.get_connection('SOME_CONN'), Graph)

    def test_bound_connection_all_params(self):
        app, client = self.create_test_app(
            OGM_GRAPH_CREDENTIALS = {
                'SOME_CONN': dict(
                    HOST = 'localhost',
                    USER = 'neo4j',
                    PASSWORD = 'password',
                    PORT = '7687',
                    PROTOCOL = 'bolt'),
            }
        )
        with app.app_context():
            ogm = OGM(app)
            assert isinstance(ogm.get_connection('SOME_CONN'), Graph)

    def test_connection_incomplete_graph_credentials(self):
        try:
            app, client = self.create_test_app(
                OGM_GRAPH_HOST = 'localhost',
                OGM_GRAPH_USER = 'neo4j'
            ) # no password
            with app.app_context():
                ogm = OGM(app)
                assert isinstance(ogm.graph, Graph)
        except GraphCredentialsIncompleteError:
            assert True
        else:
            assert False

    def test_connection_graph_credentials_not_found(self):
        try:
            app, client = self.create_test_app() # no password
            with app.app_context():
                ogm = OGM(app)
                assert isinstance(ogm.graph, Graph)
        except GraphCredentialsNotFoundError:
            assert True
        else:
            assert False