from unittest import TestCase

class FlaskOGMTestCase(TestCase):
    def create_test_app(self):
        app = Flask('test_app')
        ogm = OGM(app)
        return app, ogm
