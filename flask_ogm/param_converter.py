from functools import wraps
import inspect

from .graph import OGM

from flask_ogm.errors import ParamConverterIllegalArgumentException


ogm = OGM()


def resolve_fqn_to_object(fqn):
    """Resolve a string to a callable
    """
    module_name, dot, class_name = fqn.rpartition('.')
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)


class ParamConverter(object):
    """Convert function arguments which contain lookup values
    into py2neo.ogm.GraphObjects or collections thereof.
    """

    DEFAULT_CONSTRUCTOR_METHOD = 'select'

    def __init__(self, graph_object=None, constructor=None, param=None,
                 select_on=None, on_not_found=404, bind=None,
                 check_unique=False, on_more_than_one=None, single=True,
                 inject_old_kwarg_as=None):
        """Decorator for Flask controllers. Will convert a parameter to
        either a GraphObject or a collection of GraphObject based on
        a query to the graph. If no object is found, it will act as
        instructed, by default, returning a 404.

        Use graph_object and / or constructor to specify a constructor
        function which takes the

        :param graph_object: class to return instances of, usually
                             a py2neo.ogm.GraphObject but can be custom
                             so long as it implements default method
                             if no constructor specified
        :param constructor: reference to the method used query the
                            graph, str or callable, if str then can be
                            either fully qualified reference to a
                            function the attr of the graph_object.
        :param param: kwarg index to use to query the graph - will be
                      replaced by the return of the query
        :param select_on: if specified, the param will not be passed to
                          the constructor when called, but added onto
                          the constructor using where(select_on = x)
        :param on_not_found: what to return when no objects are found,
                             can be callable, int (HTTP status) or
                             str, if None, will return 404
        :param on_more_than_one: if unique is True, what to return
                                 if >1 argument is found, if None, 500
        :param bind: the bind to search using with ogm.get_connection,
                     default if None
        :param check_unique: if True when single is True, will check
                             that only 1 object is returned
        :param inject_old_kwarg_as: if a string, the original value of
                                    param will be injected into the
                                    decorated function. The string must
                                    relate to a kwarg in the decorated
                                    function.
        :return: the function it is decorating
        """
        # save the bind
        self.bind = bind

        # some illogical argument combinations need to be weeded out early
        if not single and on_more_than_one is not None:
            raise ParamConverterIllegalArgumentException(
                'MULTIPLE_AND_ON_>1_SET'
            )

        if not single and check_unique:
            raise ParamConverterIllegalArgumentException(
                'MULTIPLE_AND_CHECK_UNIQUE'
            )

        if param is None:
            raise ParamConverterIllegalArgumentException(
                'PARAM_NOT_SPECIFIED'
            )

        if not isinstance(param, str):
            raise ParamConverterIllegalArgumentException(
                'PARAM_MUST_BE_STRING'
            )

        if inject_old_kwarg_as == param:
            raise ParamConverterIllegalArgumentException(
                'CANNOT_REINJECT_OLD_PARAM'
            )

        # work out the constructor
        # we only need the constructor
        self.constructor = self.resolve_constructor(
            constructor=constructor,
            graph_object=graph_object)

        # work out the return type - is it a list or a single value?
        self.single = bool(single)

        # what do we do if it's not found?
        self.on_not_found = self.resolve_to_return_callable(on_not_found)

        # do we worry if we find > 1 node?
        if single and check_unique:
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
        self.inject_old_kwarg_as = inject_old_kwarg_as

        self.select_on = select_on

    def __call__(self, f):
        """Make the db query and inject it into the function"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            # is the param in the kwargs?
            if self.param not in kwargs:
                raise ParamConverterIllegalArgumentException(
                    'PARAM_NOT_FOUND_IN_KWARGS'
                )
            search_value = kwargs[self.param]

            # get the graph
            graph = ogm.get_connection(bind=self.bind)
            if self.select_on is None:
                q = self.constructor(graph, search_value)
            else:
                # use where on the default constructor
                # spoof kwargs using dictionary unpacking
                q = self.constructor(graph).where(**{
                    self.select_on: search_value
                })

            # this should return an iterable
            try:
                d = list(q)
            except TypeError:
                raise ParamConverterIllegalArgumentException(
                    'CONSTRUCTOR_MUST_RETURN_ITERABLE'
                ).append_to_message(repr(q))

            # did we find anything?
            if len(d) == 0:
                # no
                return self.on_not_found()

            # do we worry about having > 1 result`
            if len(d) > 0 and self.single and self.check_unique:
                return self.on_more_than_one()

            # inject the results
            if self.single:
                kwargs[self.param] = d[0]
            else:
                kwargs[self.param] = d

            # reinject old results?
            if self.inject_old_kwarg_as is not None \
               and self.inject_old_kwarg_as not in kwargs:
                raise ParamConverterIllegalArgumentException(
                    'REINJECT_OLD_PARAM_MUST_BE_KWARG'
                )
            elif self.inject_old_kwarg_as is not None:
                kwargs[self.inject_old_kwarg_as] = search_value

            return f(*args, **kwargs)

        return wrapper

    @staticmethod
    def resolve_to_return_callable(r):
        """Returns a callable which is called which can be called to
        provide the makings of a flask response.
        """
        if callable(r):
            return r

        def wrapper():
            return r

        return wrapper

    def resolve_constructor(self, constructor=None, graph_object=None):
        """Works out the constructor method to be used to run the query
        """
        # is the graph object a string ref?
        if isinstance(graph_object, str):
            # yes`
            try:
                resolved_object = resolve_fqn_to_object(graph_object)
            except ImportError:
                raise ParamConverterIllegalArgumentException(
                    'GRAPH_OBJECT_FQN_NOT_FOUND'
                ).append_to_message(graph_object)
            except ValueError:
                raise ParamConverterIllegalArgumentException(
                    'IMPORT_REFERENCES_MUST_BE_FQN'
                ).append_to_message(graph_object)
            graph_object = resolved_object

        # is it a callable?
        if callable(constructor) and graph_object is None:
            # yes
            return constructor
        elif graph_object is not None and callable(constructor):
            raise ParamConverterIllegalArgumentException(
                'CONSTRUCTOR_SHOULD_NOT_BE_CALLABLE'
            ).append_to_message(repr(constructor))

        # no, is it string reference to a callable?
        if isinstance(constructor, str) and '.' in constructor:
            try:
                resolved_object = resolve_fqn_to_object(constructor)
            except ImportError:
                # reference not found
                raise ParamConverterIllegalArgumentException(
                    'CONSTRUCTOR_FQN_NOT_FOUND'
                ).append_to_message(str(constructor))
            except ValueError:
                raise ParamConverterIllegalArgumentException(
                    'IMPORT_REFERENCES_MUST_BE_FQN'
                ).append_to_message(str(constructor))
            if not callable(resolved_object):
                raise ParamConverterIllegalArgumentException(
                    'CONSTRUCTOR_FQN_NOT_CALLABLE'
                ).append_to_message(str(constructor))
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
                    'CONSTRUCTOR_ATTR_NOT_FOUND'
                )
            if not callable(constructor_attr):
                raise ParamConverterIllegalArgumentException(
                    'CONSTRUCTOR_ATTR_NOT_CALLABLE'
                )
            return constructor_attr

        # something very wrong?
        if constructor is not None:
            # yes
            raise ParamConverterIllegalArgumentException(
                'INVALID_CONSTRUCTOR_ARGUMENT'
            ).append_to_message(repr(constructor))

        # constructor is None
        if graph_object is None:
            # so if graph_object: we can't produce a query
            raise ParamConverterIllegalArgumentException(
                'NO_CALLABLE_CONSTRUCTOR_FOUND'
            )

        # is it the default constructor?
        try:
            return getattr(graph_object, self.DEFAULT_CONSTRUCTOR_METHOD)
            # yes
        except AttributeError:
            # no
            raise ParamConverterIllegalArgumentException(
                'DEFAULT_CONSTRUCTOR_NOT_FOUND'
            ).append_to_message(repr(graph_object))

        # code should never run past here
        assert False  # pragma: no cover
