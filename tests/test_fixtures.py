from collections import namedtuple
from unittest import TestCase

from .fixtures import *

mock_graph_object = namedtuple('MockGraphObject', 'a')

class WidgetCollectionTestCase(TestCase):
    MOCK_LIST_DATA = [mock_graph_object(1), mock_graph_object(2)]
    def test_constructor(self):
        wc = WidgetCollection(self.MOCK_LIST_DATA)
        assert repr(self.MOCK_LIST_DATA) == repr(wc)

    def test_iter_interface(self):
        wc = WidgetCollection(self.MOCK_LIST_DATA)
        assert [x for x in wc] == self.MOCK_LIST_DATA

    def test_support_indexing(self):
        wc = WidgetCollection(self.MOCK_LIST_DATA)
        assert wc[0] == wc.data[0]

    def test_where(self):
        wc = WidgetCollection(self.MOCK_LIST_DATA)
        l = [x for x in self.MOCK_LIST_DATA if x.a == 1]
        assert list(wc.where(a = 1)) == l

class WidgetTestCase(TestCase):
    def test_iter_interface_for_queries(self):
        assert len(list(Widget.mock_select(None))) == len(Widget.MOCK_DATA)

    def test_select_on_primary_value(self):
        assert Widget.mock_select(None, 1)[0].name == 'Widget 1'

    def test_select_on_property(self):
        widget = Widget.mock_select(None).where(name = 'Widget 1')[0]
        assert widget.name == 'Widget 1'

    def test_wrap(self):
        d = { 'unique_id': 1, 'name': 'Test Widget' }
        w = Widget.mock_wrap(d)
        assert w.unique_id == d['unique_id']
        assert w.name == d['name']
