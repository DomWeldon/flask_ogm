from unittest import TestCase

from flask_ogm.errors import ParamConverterIllegalArgumentException

message_key = 'CONSTRUCTOR_SHOULD_NOT_BE_CALLABLE'


class ParamConverterIllegalArgumentExceptionTestCase(TestCase):
    def test_init_set_message(self):
        pce = ParamConverterIllegalArgumentException(message_key)
        assert pce.message == pce.ILLEGAL_ARGUMENT_MESSAGES[message_key]

    def test_append(self):
        pce = ParamConverterIllegalArgumentException(message_key)
        pce.append_to_message('woof!')
        new_message = pce.ILLEGAL_ARGUMENT_MESSAGES[message_key] + 'woof!'
        assert pce.message == new_message

    def test_append_non_string(self):
        pce = ParamConverterIllegalArgumentException(message_key)
        pce.append_to_message(123)
        new_message = pce.ILLEGAL_ARGUMENT_MESSAGES[message_key] + '123'
        assert pce.message == new_message

    def test_output_as_str(self):
        pce = ParamConverterIllegalArgumentException(message_key)
        assert str(pce) == pce.ILLEGAL_ARGUMENT_MESSAGES[message_key]
