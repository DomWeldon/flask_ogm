from functools import wraps

from py2neo.ogm import GraphObject
from flask import current_app

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
    'CONSTRUCTOR_NOT_CALLABLE': (
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
        'The default constructor, GraphObject.select, is not implemented '
        'for this graph_object: '
    )
}

class ParamConverterIllegalArgumentException(ValueError): pass

def resolve_fqn_to_callable(fqn):
    """Resolve a string to a callable
    """
    module_name, _, class_name = fqn.rpartition(".")
    module = __import__(module_name, fromlist=".")
    c = getattr(module, class_name)
    if not callable(c):
        raise TypeError()
    return c

class ParamConverter(object):
    """Convert function arguments which contain lookup values
    into py2neo.ogm.GraphObjects or collections thereof.
    """
    def __init__(self, graph_object = None, constructor = None, param = None,
                 select_on = None, on_not_found = None, bind = None,
                 on_more_than_one = None, unique = True, order_by = None,
                 inject_old_kwarg_as = None):
        """Decorator for Flask controllers. Will convert a parameter to
        either a GraphObject or a collection of GraphObject based on
        a query to the graph. If no object is found, it will act as
        instructed, by default, returning a 404.

        :param graph_object: GraphObject to return instances of
        :param constructor: reference to the method used query the
                            graph, str or callable, if str then can be
                            either fully qualified reference to a
                            function the attr of the graph_object
        :param param: kwarg index to use to query the graph - will be
                      replaced by the return of the query
        :param property: if no constructor specified, the property to
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

        BAD ARGUMENT COMBOS:
         - graph_object and constructor not set
         - graph_object set and str(constructor) has dot in it
         - graph_object set and constructor is callable
        """
        # work out the constructor
        # we only need the constructor
        self.constructor = self.resolve_constructor(
            constructor = constructor,
            graph_object = graph_object)


        # work out the return type - is it a list or a single value?

        # what do we do if it's not found?

        # do we worry if we find > 1 node?

        # do we inject the old param?


        return self

    def __call__(self, *args, **kwargs):
        """"""
        pass

    def resolve_constructor(self, constructor, graph_object):
        # is it a callable?
        if callable(constructor) and graph_object is None:
            # yes
            self.constructor = constructor
        elif graph_object is not None:
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
                self.constructor = resolve_fqn_to_callable(constructor)
            except ImportError:
                # reference not found
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['CONSTRUCTOR_FQN_NOT_FOUND']
                    + str(constructor)
                )
            except TypeError:
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['CONSTRUCTOR_NOT_CALLABLE']
                    + str(constructor)
                )

        # a reference to a method on graph_object?
        if isinstance(constructor, str) \
           and isinstance(graph_object, GraphObject):
           # should be
            try:
                self.constructor = getattr(graph_object, constructor)
                # it is!
            except AttributeError:
                # but it isn't!
                raise ParamConverterIllegalArgumentException(
                    ILLEGAL_ARGUMENT_MESSAGES['CONSTRUCTOR_ATTR_NOT_FOUND']
                )

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
            self.constructor = graph_object.select
            # yes
        except AttributeError:
            # no
            raise ParamConverterIllegalArgumentException(
                'DEFAULT_CONSTRUCTOR_NOT_FOUND'
                + repr(graph_object)
            )

        return True
