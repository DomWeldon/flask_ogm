from py2neo import Graph

try:
    from flask_ogm.param_converter import *  # typical import
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from flask_ogm.param_converter import *


from .util import FlaskOGMTestCase
from .fixtures import Widget

class ParamConverterTestCase(FlaskOGMTestCase): pass

class ResolveFQNToCallableTestCase(ParamConverterTestCase):
    """Tesst resolve_fqn_to_object to ensure it imports correctly
    """
    def test_one_dot(self):
        c = resolve_fqn_to_object('py2neo.ogm')
        from py2neo import ogm
        assert c == ogm

    def test_two_dots(self):
        c = resolve_fqn_to_object('tests.fixtures.Widget')
        assert c == Widget

class ResolveConstructorTestCase(ParamConverterTestCase):
    """Test ParamConverter.resolve_constructor()
    """
    def check_for_exception_message(self, message_key, **kwargs):
        """Check that the right exception / message is produced for
        given combination of arguments
        """
        # call the function to produce the exception
        try:
            pc = ParamConverter(**kwargs)
        except ParamConverterIllegalArgumentException as e:
            # exception produced, is it the right message?
            # messages can have values appended to them...
            desired_message = ILLEGAL_ARGUMENT_MESSAGES[message_key]
            # test passes if yes, fails if not
            assert str(e)[0:len(desired_message)] == desired_message
        else:
            # no exception produced, test fails
            assert False
    # check all the ways it's meant to go wrong...
    def test_constructor_should_not_be_callable(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_SHOULD_NOT_BE_CALLABLE',
            constructor = lambda x: x,
            graph_object = Widget
        )

    def test_constructor_fqn_not_found(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_FQN_NOT_FOUND',
            constructor = 'this.does.not.exist')

    def test_constructor_not_callable(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_FQN_NOT_CALLABLE',
            constructor = 'tests.fixtures')

    def test_constructor_attr_not_found(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_ATTR_NOT_FOUND',
            constructor = 'not_implemented',
            graph_object = Widget
        )

    def test_constructor_attr_not_callable(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_ATTR_NOT_CALLABLE',
            graph_object = Widget,
            constructor = '__primarykey__'
        )

    def test_constructor_invalid(self):
        self.check_for_exception_message(
            'INVALID_CONSTRUCTOR_ARGUMENT',
            graph_object = Widget,
            constructor = {}
        )

    def test_constructor_invalid2(self):
        self.check_for_exception_message(
            'INVALID_CONSTRUCTOR_ARGUMENT',
            constructor = 'woof'
        )

    def test_graph_object_and_constructor_not_set(self):
        self.check_for_exception_message('NO_CALLABLE_CONSTRUCTOR_FOUND')

    def test_default_constructor_not_found(self):
        self.check_for_exception_message(
            'DEFAULT_CONSTRUCTOR_NOT_FOUND',
            graph_object = object()
        )

    # check all the ways its meant to go right
    def test_simple_object(self):
        pc = ParamConverter(graph_object = Widget)
        assert pc.constructor == Widget.select

    def test_graph_object_with_constructor_attr(self):
        pc = ParamConverter(graph_object = Widget,
                            constructor = 'custom_constructor')
        assert pc.constructor == Widget.custom_constructor

    def test_str_to_import_with_default_constructor(self):
        pc = ParamConverter(graph_object = 'tests.fixtures.Widget')
        assert pc.constructor == Widget.select

    def test_str_to_import_with_custom_constructor(self):
        pc = ParamConverter(graph_object = 'tests.fixtures.Widget',
                            constructor = 'custom_constructor')
        assert pc.constructor == Widget.custom_constructor

    def test_simple_callable(self):
        my_callable = lambda x: x
        pc = ParamConverter(constructor = my_callable)
        assert pc.constructor == my_callable
