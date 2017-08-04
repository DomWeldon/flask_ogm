from flask import abort
from functools import wraps
import inspect
from werkzeug.http import HTTP_STATUS_CODES

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
        instructed, by default returning a 404. Use graph_object
        and/or constructor arguments to specify a callable which will
        take the kwarg[param], and use it to search for a node based
        on its value.

        :param graph_object: Class to return instances of, usually
                             a `py2neo.ogm.GraphObject` but can be
                             custom class, or a string referencing
                             that object (e.g., `src.models.Widget`).
                             If a string is set for `constructor`,
                             `ParamConverter` will look for a method on
                             this object with that name, if
                             `constructor` is None, then the
                             `DEFAULT_CONSTRUCTOR_METHOD` (set as
                             select) will be used instead. If
                             `graph_object` is `None`, then
                             `constructor` must be specified.
        :param constructor: A callable, or reference to a callable to
                            query the graph and return an iterable of
                            GraphObjects. If `graph_object` is
                            specified, and this value is a string,
                            `ParamConverter` will search for a method
                            named after this string on graph_object.
        :param param: The key of the keyword argument to act on.
                      `ParamConverter` will pass the value of this arg
                      to the constructor, and replace it with what is
                      returned by the constructor.
        :param select_on: If graph_object is if specified, and this
                          value is a string, the param will not be
                          passed to the constructor when called, but
                          handed to the query using the `where()`
                          method, i.e. for `select_on='name'`:`
                          `Widget.select(graph).where(name=x)`
        :param on_not_found: What to return when no objects are found,
                             can be callable, int (HTTP status) or
                             str. If None, will return 404.
        :param on_more_than_one: If `check_unique` is True and `single`
                                 is False, what to return if >1 match
                                 is returned by the constructor. If
                                 `None` then will return status 500.
        :param single: Bool, whether to return a the first result from
                       `constructor`, or all results as a list
                       (`constructor` must return an iterable). Can
                       be used in conjunction with `check_unique` and
                       `on_more_than_one` to ensure values are unique
                       in the graph.
        :param bind: the bind to search using with
                     `ogm.get_connection()`, `ogm.graph` is used if
                     None.
        :param check_unique: if True when single is True, will check
                             that only 1 object is returned. If >1
                             object, then will act according to
                             `on_more_than_one`
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
            if len(d) > 1 and self.single and self.check_unique:
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
            try:
                if int(r) in HTTP_STATUS_CODES:
                    abort(r)
            except ValueError:
                pass

            return str(r)

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
