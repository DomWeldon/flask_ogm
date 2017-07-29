from .util import Flask, FlaskOGMTestCase

class TestTestCase(FlaskOGMTestCase):
    def test_create_test_app(self):
        app, client = self.create_test_app(SOME_PARAM = 'value')
        assert isinstance(app, Flask)
        assert'SOME_PARAM' in app.config and app.config['SOME_PARAM'] == 'value'
