from py2neo.ogm import GraphObject, Property


def custom_widget_finding_function():  # pragma: no cover
    """Used to test string resolution to a callable."""
    pass  # pragma: no cover


class Widget(GraphObject):
    """A dummy GraphObject used as a fixture in unit tests, and to show
    ParamConverter's behaviour in the documentation."""
    unique_id = Property()
    """Unique integer field."""
    name = Property()
    """Unique string field"""
    colour = Property()
    """Non-unique field"""
    __primarykey__ = 'unique_id'
    """Primary field name to select on"""

    MOCK_DATA = [
        {
            'unique_id': 1,
            'name': 'Widget 1',
            'colour': 'red',
        },
        {
            'unique_id': 2,
            'name': 'Widget 2',
            'colour': 'red',
        },
        {
            'unique_id': 3,
            'name': 'Widget 3',
            'colour': 'blue',
        },
    ]

    def as_dict(self):
        """Return the public properties of the node as a dictionary"""
        return {
            k: getattr(self, k)
            for k in ['unique_id', 'name', 'colour']
        }

    @classmethod
    def custom_constructor(cls, graph, property):  # pragma: no cover
        """Never runs, only used in tests that check this method is
        present
        """
        pass  # pragma: no cover

    @classmethod
    def return_non_iter(cls, *args, **kwargs):
        """Required for checking an exception is raised when a
        constructor returns a non-iterable
        """
        return None

    @classmethod
    def search_on_name(cls, graph, name):
        """Use cypher to search for a Widget whose name STARTS WITH
        name and return results as an iterable.
        """
        q = 'MATCH (_:Widget) WHERE _.name STARTS WITH {n} RETURN _'
        results = graph.run(q, {'n': name}).data()
        return [cls.wrap(r['_']) for r in results]
