class FlaskOGMError(Exception):
    """Base class for errors in this module."""
    pass


class GraphCredentialsIncompleteError(FlaskOGMError):
    pass


class GraphCredentialsNotFoundError(FlaskOGMError):
    pass


class OutOfApplicationContextError(FlaskOGMError):
    pass


class DefaultGraphCredentialsUnclearError(FlaskOGMError):
    pass


class ParamConverterIllegalArgumentException(ValueError):
    ILLEGAL_ARGUMENT_MESSAGES = {
        'CONSTRUCTOR_SHOULD_NOT_BE_CALLABLE': (
            'Constructor cannot be callable when graph_object '
            'is specified: constructor is '
        ),
        'CONSTRUCTOR_FQN_NOT_FOUND': (
            'Your constructor, specified as a fully qualified string to '
            'import, was not found: '
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
            'References to an object to import must be fully qualified '
            'names, no possible module found for: '
        ),
        'GRAPH_OBJECT_FQN_NOT_FOUND': (
            'Your graph object, specified as a fully qualified string to'
            'import, was not found: '
        ),
        'MULTIPLE_AND_ON_>1_SET': (
            'You have set single = False, so requesting more than one result '
            'to be returned, however, you have also specified a status code '
            'or exception to be raised or returned when  >1 result is found.'
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
        'PARAM_NOT_FOUND_IN_KWARGS': (
            'The specified param was not found in the kwargs of the '
            'decorated function.'
        ),
        'CONSTRUCTOR_MUST_RETURN_ITERABLE': (
            'Your constructor returned did not return an iterable. Your '
            'constructor must return an iterable even when no results are '
            'found. Your constructor returned: '

        ),
        'REINJECT_OLD_PARAM_MUST_BE_KWARG': (
            'The value to reinject the original value of the param must '
            'be specified as a keyword argument in the decorated function.'
        ),
    }

    def __init__(self, message):
        self.message = self.ILLEGAL_ARGUMENT_MESSAGES[message]

    def append_to_message(self, value):
        self.message += str(value)

        return self

    def __str__(self):
        return self.message
