from flask import Flask
try:
    from flask_ogm import OGM  # The typical way to import flask-cors
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from flask_ogm import OGM

from .util import FlaskOGMTestCase

class GraphTestCase(FlaskOGMTestCase):
    def test_default_connection_simple(self):
        app, ogm = self.create_test_app()
        assert True
