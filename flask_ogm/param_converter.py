from functools import wraps
import inspect

from flask import abort, current_app

# import application context - safe vor pre v.09

from .graph import OGM

# One could debate whether this is pythonic - specifying all the ways the
# tool could be called correctly and then listing each with an informative
# error message. The aim, however, is to produce a useful - handy - little
# method that fits lots of use cases. The error messages here provide useful
# references for unit tests, and hopefully will guide users when having made
# an error. They should also reveal the thinking behind any bugs which are
# not picked up in tests, making for an easier fix.
ILLEGAL_ARGUMENT_MESSAGES = {
    'CONSTRUCTOR_SHOULD_NOT_BE_CALLABLE': (
        'Constructor cannot be callable when graph_object '
        'is specified: constructor is '
    ),
    'CONSTRUCTOR_FQN_NOT_FOUND': (
        'Your constructor, specified as a fully qualified string to import, '
        'was not found: '
    ),
    'CONSTRUCTOR_ATTR_NOT_FOUND': (
        'Your constructor, specified as a string point to an attribute '
        'of your graph_object, was not found: '
    ),
    'CONSTRUCTOR_ATTR_NOT_CALLABLE': (
        'Your constructor, specified as a string point to an attribute '
        'of your graph_object, was found but is not callable: '
    ),
    'CONSTRUCTOR_FQN_NOT_CALLABLE': (
        'Constructor method not callable:'
    ),
    'NO_CALLABLE_CONSTRUCTOR_FOUND': (
        'graph_object and constructor cannot both be None. '
        'You must indicate a constructor to be used as a constructor.'
    ),
    'INVALID_CONSTRUCTOR_ARGUMENT': (
        'Constructor invalid: '
    ),
    'DEFAULT_CONSTRUCTOR_NOT_FOUND': (
        'The default constructor, `select`, is not implemented '
        'for this graph_object: '
    ),
    'IMPORT_REFERENCES_MUST_BE_FQN': (
        'References to an object to import must be fully qualified names, '
        'no possible module found for: '
    ),
    'GRAPH_OBJECT_FQN_NOT_FOUND': (
        'Your graph object, specified as a fully qualified string to import,'
        ' was not found: '
    ),
    'SELECT_ON_AND_CONSTRUCTOR_SET': (
        'You have specified a property to use in the default '
        'constructor, but have also specified a custom constructor '
        'too. You must choose one or the other.'
    ),
    'MULTIPLE_AND_ON_>1_SET': (
        'You have set single = False, so requesting more than one result '
        'to be returned, however, you have also specified a status code or '
        'exception to be raised or returned when  >1 result is found.'
    ),
    'MULTIPLE_AND_CHECK_UNIQUE': (
        'You have set single = False, so requesting more than one result '
        'to be returned, however, you have also set check_unique = True, '
        'meaning an error should be raised when >1 result is found.'
    ),
    'PARAM_NOT_SPECIFIED': (
        'You must speficy the kwarg you wish to search on and replace.'
    ),
    'PARAM_MUST_BE_STRING': (
        'The speficied parameter must be a string.'
    ),
    'CANNOT_REINJECT_OLD_PARAM': (
        'You have set the value of inject_old_kwarg_as == param'
    ),
}

class ParamConverterIllegalArgumentException(ValueError): pass

def resolve_fqn_to_object(fqn):
    """Resolve a string to a callable
    """
    module_name, dot, class_name = fqn.rpartition('.')
    module = __import__(module_name, fromlist = [class_name])
    return getattr(module, class_name)

class ParamConverter(object):
    """Convert function arguments which contain lookup values
    into py2neo.ogm.GraphObjects or collections thereof.
    """

    DEFAULT_CONSTRUCTOR_METHOD = 'select'

    def __init__(self, graph_object = None, constructor = None, param = None,
                 select_on = None, on_not_found = 404, bind = None,
                 check_unique = False, on_more_than_one = None, single = True,
                 inject_old_kwarg_as = None, call_query_method = 'data'):
        """Decorator for Flask controllers. Will convert a parameter to
        either a GraphObject or a collection of GraphObject based on
        a query to the graph. If no object is found, it will act as
        instructed, by default, returning a 404.

        :param graph_object: class to return instances of, usually
                             a py2neo.ogm.GraphObject but can be custom
                             so long as it implements default method
                             if no constructor specified
        :param constructor: reference to the method used query the
                            graph, str or callable, if str then can be
                            either fully qualified reference to a
                            function the attr of the graph_object
        :param param: kwarg index to use to query the graph - will be
                      replaced by the return of the query
        :param select_on: if no constructor specified, the property to
                          query on, i.e., "__id__", if None then
                          graph_object.__primarykey__ is used
        :param on_not_found: what to return when no objects are found,
                             can be callable, int (HTTP status) or
                             str, if None, will return 404
        :param on_more_than_one: if unique is True, what to return
                                 if >1 argument is found, if None, 500
        :param bind: the bind to search using with ogm.get_connection,
                     default if None
        :param unique: whether there should be only 1 result for the
                       query, if false will return a
                       list, if true will return a single GraphObject
        :param order_by: how to order the query (and return) if unique
                         is False
        :param inject_old_kwarg_as: what and whether to inject the
                                    initial value of param as into the
                                    function, str if set, if None then
                                    param + '_', if False then no param
                                    injected.
        :return: the function it is decorating
        """
        # some illogical argument combinations need to be weeded out early
        if select_on is not None and constructor is not None:
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['SELECT_ON_AND_CONSTRUCTOR_SET']
            )

        if single == False and on_more_than_one is not None:
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['MULTIPLE_AND_ON_>1_SET']
            )

        if single == False and check_unique == True:
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['MULTIPLE_AND_CHECK_UNIQUE']
            )

        if param is None:
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['PARAM_NOT_SPECIFIED']
            )

        if not isinstance(param, str):
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['PARAM_MUST_BE_STRING']
            )

        if inject_old_kwarg_as == param:
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['CANNOT_REINJECT_OLD_PARAM']
            )

        # work out the constructor
        # we only need the constructor
        self.constructor = self.resolve_constructor(
            constructor = constructor,
            graph_object = graph_object)

        # work out the return type - is it a list or a single value?
        self.single = bool(single)

        # what do we do if it's not found?
        self.on_not_found = self.resolve_to_return_callable(on_not_found)

        # do we worry if we find > 1 node?
        if single == True and check_unique == True:
            # yes
            if on_more_than_one is not None:
                omto = self.resolve_to_return_callable(on_more_than_one)
            else:
                omto = self.resolve_to_return_callable(500)
            self.on_more_than_one = omto
            self.check_unique = True
        else:
            self.check_unique = False

        # do we inject the old param?
        self.param = param
        if inject_old_kwarg_as is None:
            self.inject_old_kwarg_as = '_' + param
        else:
            self.inject_old_kwarg_as = inject_old_kwarg_as

    def __call__(self, *args, **kwargs):
        """"""
        pass

    @staticmethod
    def resolve_to_return_callable(on_not_found):
        """Returns a callable which is called which can be called to
        provide the makings of a flask response.
        """
        if callable(on_not_found):
            return on_not_found

        def wrapper():
            return on_not_found

        return wrapper

    def resolve_constructor(self, constructor = None, graph_object = None):
        """Works out the constructor method to be used to run the query
        """
        # is the graph object a string ref?
        if isinstance(graph_object, str):
            # yes`
            try:
                resolved_object = resolve_fqn_to_object(graph_object)
            except ImportError:
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['GRAPH_OBJECT_FQN_NOT_FOUND']
                    + graph_object
                )
            except ValueError:
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['IMPORT_REFERENCES_MUST_BE_FQN']
                    + graph_object
                )
            graph_object = resolved_object

        # is it a callable?
        if callable(constructor) and graph_object is None:
            # yes
            return constructor
        elif graph_object is not None and callable(constructor):
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES[
                    'CONSTRUCTOR_SHOULD_NOT_BE_CALLABLE'
                ]
                + repr(constructor)
            )

        # no, is it string reference to a callable?
        if isinstance(constructor, str) and '.' in constructor:
            try:
                # copy py2neo code here
                resolved_object = resolve_fqn_to_object(constructor)
            except ImportError:
                # reference not found
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['CONSTRUCTOR_FQN_NOT_FOUND']
                    + str(constructor)
                )
            except ValueError:
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['IMPORT_REFERENCES_MUST_BE_FQN']
                    + str(constructor)
                )
            if not callable(resolved_object):
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['CONSTRUCTOR_FQN_NOT_CALLABLE']
                    + str(constructor)
                )
            return resolved_object

        # a reference to a method on graph_object?
        if isinstance(constructor, str) \
           and inspect.isclass(graph_object):
            # should be
            try:
                constructor_attr = getattr(graph_object, constructor)
                # it is!
            except AttributeError:
                # but it isn't!
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['CONSTRUCTOR_ATTR_NOT_FOUND']
                )
            if not callable(constructor_attr):
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['CONSTRUCTOR_ATTR_NOT_CALLABLE']
                )
            return constructor_attr

        # something very wrong?
        if constructor is not None:
            # yes
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['INVALID_CONSTRUCTOR_ARGUMENT']
                + repr(constructor)
            )

        # constructor is None
        if graph_object is None:
            # so if graph_object: we can't produce a query
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['NO_CALLABLE_CONSTRUCTOR_FOUND']
            )

        # is it the default constructor?
        try:
            return getattr(graph_object, self.DEFAULT_CONSTRUCTOR_METHOD)
            # yes
        except AttributeError:
            # no
            raise ParamConverterIllegalArgumentException(
                ILLEGAL_ARGUMENT_MESSAGES['DEFAULT_CONSTRUCTOR_NOT_FOUND']
                + repr(graph_object)
            )

        # code should never run past here
        assert False
