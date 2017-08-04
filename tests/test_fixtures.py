from flask_ogm import OGM

from .test_param_converter import ParamConverterTestCase
from .fixtures import Widget

ogm = OGM()


class WidgetTestCase(ParamConverterTestCase):
    def test_widget_as_dict(self):
        """Check as_dict method behaves as expected"""
        with self.get_app_context():
            widget = Widget.select(ogm.graph, 1).first().as_dict()
            assert Widget.MOCK_DATA[0] == widget

    def test_widget_has_dummy_methods(self):
        try:
            assert Widget.return_non_iter
            assert Widget.custom_constructor
        except AttributeError:
            assert False

    def test_search_on_name(self):
        with self.get_app_context():
            widgets = Widget.search_on_name(ogm.graph, 'Widget')
            assert len(widgets) == 3
