from py2neo import Graph
from werkzeug.exceptions import NotFound

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

class ParamConverterTestCase(FlaskOGMTestCase):
    def get_app_context(self):
        """Provided since we need an app context to test anything using
        OGM. However, widget is designed to return dummy data, so we
        don't ever need to connect to the db.
        Don't worry about these config details.
        """
        app, client = self.create_test_app(
            OGM_GRAPH_HOST = 'localhost',
            OGM_GRAPH_USER = 'neo4j',
            OGM_GRAPH_PASSWORD = 'password'
        )
        return app.app_context()

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

class CallDecoratorTestCase(ParamConverterTestCase):

    @ParamConverter(graph_object = Widget, param = 'unique_id')
    def mock_controller_kwarg_missing(self, some_arg = None):
        pass

    def test_param_missing_from_kwargs(self):
        try:
            self.mock_controller_kwarg_missing(widget = 1)
        except ParamConverterIllegalArgumentException as e:
            message = ILLEGAL_ARGUMENT_MESSAGES['PARAM_NOT_FOUND_IN_KWARGS']
            assert message[0:len(message)] == str(e)[0:len(message)]
        else:
            assert False

    @ParamConverter(constructor = Widget.return_non_iter, param = 'widget')
    def mock_controller_non_iterable(self, widget = None):
        pass

    def test_constructor_returns_non_iterable(self):
        try:
            with self.get_app_context():
                self.mock_controller_non_iterable(widget = 1)
        except ParamConverterIllegalArgumentException as e:
            message = ILLEGAL_ARGUMENT_MESSAGES[
                'CONSTRUCTOR_MUST_RETURN_ITERABLE'
            ]
            assert message[0:len(message)] == str(e)[0:len(message)]
        else:
            assert False

    @ParamConverter(constructor = Widget.mock_select, param = 'widget')
    def mock_controller_select_simple(self, widget = None):
        return widget

    def test_select_simple(self):
        with self.get_app_context():
            f = Widget.MOCK_DATA[0]
            widget = self.mock_controller_select_simple(
                widget = f['unique_id']
            )
            assert widget.unique_id == f['unique_id']

    @ParamConverter(constructor = Widget.mock_select, param = 'widget',
                    select_on = 'name')
    def mock_controller_select_on_property(self, widget = None):
        return widget

    def test_select_on_property(self):
        with self.get_app_context():
            widget = self.mock_controller_select_on_property(widget = 'Widget 1')
            assert widget.name == 'Widget 1'

    @ParamConverter(constructor = Widget.mock_select, param = 'widgets',
                    single = False, select_on = 'colour')
    def mock_controller_select_multiple(self, widgets = None):
        return widgets

    def test_select_multiple(self):
        with self.get_app_context():
            widgets = self.mock_controller_select_multiple(widgets = 'red')
            assert len(widgets) == 2

    @ParamConverter(constructor = Widget.mock_select, param = 'widget',
                    on_not_found = 404)
    def mock_controller_not_found(self, widget = None):
        return False

    def test_not_found(self):
        with self.get_app_context():
            widget = self.mock_controller_not_found(widget = -1)
            assert widget == 404

    @ParamConverter(constructor = Widget.mock_select, param = 'widget',
                    check_unique = True, on_more_than_one = 500,
                    select_on = 'colour')
    def mock_controller_check_unique(self, widget = None):
        return widget

    def test_check_unique(self):
        with self.get_app_context():
            widget = self.mock_controller_check_unique(widget = 'red')
            assert widget == 500

    @ParamConverter(constructor = Widget.mock_select, param = 'widget',
                    inject_old_kwarg_as = '_widget')
    def mock_controller_reinject_unspecified_kwarg(self, widget = None):
        return widget

    def test_reinject_unspecified_kwarg(self):
        try:
            with self.get_app_context():
                self.mock_controller_reinject_unspecified_kwarg(widget = 1)
        except ParamConverterIllegalArgumentException as e:
            message = ILLEGAL_ARGUMENT_MESSAGES[
                'REINJECT_OLD_PARAM_MUST_BE_KWARG'
            ]
            assert message[0:len(message)] == str(e)[0:len(message)]
        else:
            assert False

    @ParamConverter(constructor = Widget.mock_select, param = 'widget',
                    inject_old_kwarg_as = '_widget')
    def mock_controller_reinject_kwarg(self, widget = None, _widget = None):
        return widget, _widget

    def test_reinject_kwarg(self):
        with self.get_app_context():
            o, a = self.mock_controller_reinject_kwarg(widget = 1,
                                                       _widget = None)
            assert o.unique_id == 1
            assert a == 1


class CallableGeneratorsTestCase(ParamConverterTestCase):
    def test_on_more_than_one_assigned_properly(self):
        pc = ParamConverter(graph_object = Widget, single = True,
                            check_unique = True, param = 'id')
        assert pc.on_more_than_one() == 500

    def test_on_not_found_assigned_properly(self):
        pc = ParamConverter(graph_object = Widget, param = 'id')
        assert pc.on_not_found() == 404

    def test_with_int(self):
        assert ParamConverter.resolve_to_return_callable(500)() == 500

    def test_with_callable(self):
        def c():
            return NotFound()
        assert isinstance(
            ParamConverter.resolve_to_return_callable(c)(),
            NotFound)

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

class MissingOrIllogicalArgumentCombinationTestCase(ParamConverterTestCase):
    """Test for bad combinations of arguments
    """

    def test_multiple_and_more_than_one_set(self):
        self.check_for_exception_message(
            'MULTIPLE_AND_ON_>1_SET',
            single = False,
            on_more_than_one = Exception,
            param = 'id'
        )

    def test_multiple_and_check_unique(self):
        self.check_for_exception_message(
            'MULTIPLE_AND_CHECK_UNIQUE',
            single = False,
            check_unique = True,
            param = 'id'
        )

    def test_missing_param(self):
        self.check_for_exception_message('PARAM_NOT_SPECIFIED')

    def test_param_is_not_str(self):
        self.check_for_exception_message(
            'PARAM_MUST_BE_STRING',
            param = 123
        )

    def test_param_not_reinjected(self):
        self.check_for_exception_message(
            'CANNOT_REINJECT_OLD_PARAM',
            param = 'id',
            inject_old_kwarg_as = 'id'
        )

class ResolveConstructorTestCase(ParamConverterTestCase):
    """Test ParamConverter.resolve_constructor()
    """
    # check all the ways it's meant to go wrong...
    def test_constructor_should_not_be_callable(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_SHOULD_NOT_BE_CALLABLE',
            param = 'id',
            constructor = lambda x: x,
            graph_object = Widget
        )

    def test_constructor_fqn_not_found(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_FQN_NOT_FOUND',
            param = 'id',
            constructor = 'this.does.not.exist')

    def test_constructor_not_callable(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_FQN_NOT_CALLABLE',
            constructor = 'tests.fixtures',
            param = 'id')

    def test_constructor_attr_not_found(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_ATTR_NOT_FOUND',
            param = 'id',
            constructor = 'not_implemented',
            graph_object = Widget
        )

    def test_constructor_attr_not_callable(self):
        self.check_for_exception_message(
            'CONSTRUCTOR_ATTR_NOT_CALLABLE',
            param = 'id',
            graph_object = Widget,
            constructor = '__primarykey__'
        )

    def test_constructor_invalid(self):
        self.check_for_exception_message(
            'INVALID_CONSTRUCTOR_ARGUMENT',
            param = 'id',
            graph_object = Widget,
            constructor = {}
        )

    def test_constructor_invalid2(self):
        self.check_for_exception_message(
            'INVALID_CONSTRUCTOR_ARGUMENT',
            param = 'id',
            constructor = 'woof'
        )

    def test_graph_object_and_constructor_not_set(self):
        self.check_for_exception_message(
            'NO_CALLABLE_CONSTRUCTOR_FOUND',
            param = 'id',
        )

    def test_default_constructor_not_found(self):
        self.check_for_exception_message(
            'DEFAULT_CONSTRUCTOR_NOT_FOUND',
            graph_object = object(),
            param = 'id'
        )

    # check all the ways its meant to go right
    def test_simple_object(self):
        pc = ParamConverter(graph_object = Widget, param = 'id')
        assert pc.constructor == Widget.select

    def test_graph_object_with_constructor_attr(self):
        pc = ParamConverter(graph_object = Widget,
                            constructor = 'custom_constructor',
                            param = 'id')
        assert pc.constructor == Widget.custom_constructor

    def test_str_to_import_with_default_constructor(self):
        pc = ParamConverter(graph_object = 'tests.fixtures.Widget',
                            param = 'id')
        assert pc.constructor == Widget.select

    def test_str_to_import_with_custom_constructor(self):
        pc = ParamConverter(graph_object = 'tests.fixtures.Widget',
                            constructor = 'custom_constructor',
                            param = 'id')
        assert pc.constructor == Widget.custom_constructor

    def test_simple_callable(self):
        my_callable = lambda x: x
        pc = ParamConverter(constructor = my_callable, param = 'id')
        assert pc.constructor == my_callable
