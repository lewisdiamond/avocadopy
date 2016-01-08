import six
import re

is_id_re = re.compile("^[a-zA-Z][a-zA-Z0-9_\-]*\/[a-zA-Z0-9_\-:.@()+,=;$!*'%]+$")
def is_id(value):
    if not isinstance(value, six.string_types):
        return False
    return is_id_re.match(value) is not None

