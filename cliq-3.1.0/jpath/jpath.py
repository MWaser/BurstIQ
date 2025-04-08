from typing import Any

from jsonpath_ng import parse


class JPath(object):
    """
    Helper method for performing a path in one-step
    """

    @staticmethod
    def eval(data: dict, path: str, default: Any = None) -> Any:
        # shortcut allows caller not to specify root $.
        if not path.startswith('$.'):
            path = '$.' + path

        expr = parse(path)
        match = expr.find(data)
        if match is None or len(match) == 0:
            return default

        # strip out all the fluff and return the value
        values = []
        for m in match:
            values.append(m.value)

        # if single array, then return a scalar
        if len(values) == 1:
            return values[0]
        else:
            return values
