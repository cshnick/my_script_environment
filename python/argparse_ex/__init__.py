import logging as log
import os

SUBPARSERS = 'subparsers'

log.basicConfig(level=log.DEBUG if 'DEBUG' in os.environ else log.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s')


class ArgparserBase(object):
    def __init__(self):
        self._args = None
        self._init_args()

    def _init_args(self):
        pass

    def main(self):
        log.debug("Self args: %s" % self._args)
        try:
            name = 'process_' + self._args.__dict__[SUBPARSERS]
            callback = getattr(self, name)
            if callback:
                callback()
        except RuntimeError as runtimeerr:
            print(runtimeerr)
        except AttributeError as e:
            print(e)
        except TypeError as e:
            print(e)
        except KeyboardInterrupt:
            exit(0)

    @staticmethod
    def log(*args, **kwargs):
        log.debug(*args, **kwargs)
