from py2neo.ogm import GraphObject, Property


def custom_widget_finding_function():  # pragma: no cover
    """Used to test string resolution to a callable."""
    pass  # pragma: no cover


class Widget(GraphObject):
    unique_id = Property()
    name = Property()
    colour = Property()  # I'm British: this is the correct spelling :P
    __primarykey__ = 'unique_id'
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

    selected_data = []

    @classmethod
    def custom_constructor(cls, graph, property):  # pragma: no cover
        """Never runs, only used in tests that check this method is
        present
        """
        pass  # pragma: no cover

    @classmethod
    def return_non_iter(cls, *args, **kwargs):
        """Required for checking an excdeption is raised when a
        constructor returns a non-iterable
        """
        return None
