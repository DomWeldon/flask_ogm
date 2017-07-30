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

class ParamConverterTestCase(FlaskOGMTestCase): pass

class ResolveConstructorTestCase(ParamConverterTestCase):
    """Test ParamConverter.resolve_constructor()
    """
    def test_graph_object_and_constructor_not_set(self):
        try:
            pc = ParamConverter()
        except ParamConverterIllegalArgumentException as e:
            assert str(e) == ILLEGAL_ARGUMENT_MESSAGES[
                'NO_CALLABLE_CONSTRUCTOR_FOUND'
            ]
        else:
            assert False

    def test_graph_constructor_fqn_not_found(self):
        try:
            pc = ParamConverter(constructor = 'src.not.here.pal')
        except ParamConverterIllegalArgumentException as e:
            assert str(e) == ILLEGAL_ARGUMENT_MESSAGES[
                'CONSTRUCTOR_FQN_NOT_FOUND'
            ]
        else:
            assert False
