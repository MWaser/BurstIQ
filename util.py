import os


class Util(object):
    @staticmethod
    def standardize_file(fn: str) -> str:
        fn = os.path.expanduser(fn)
        fn = os.path.expandvars(fn)
        fn = os.path.abspath(fn)
        return fn
