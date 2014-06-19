__author__ = 'ilia'

class term_color:
    black   = "\033[0;30m"
    red     = "\033[0;31m"
    green   = "\033[0;32m"
    yellow  = "\033[0;33m"
    blue    = "\033[0;34m"
    purple  = "\033[0;35m"
    cyan    = "\033[0;36m"
    white   = "\033[0;37m"
    reset   = "\033[0m"

def colorize(color, set_it=True):
    def color_decorator(str_func):
        def wrapped(*args, **kwargs):
            if set_it:
                return color + str_func(*args, **kwargs) + term_color.reset
            else:
                return str_func(*args, **kwargs)
        return wrapped
    return color_decorator

# Generate class corresponding to a term_color data
# Coloring given text
class Color():
    def __init__(self, text):
        self.text = text

    def as_color(self, str_color):
        if hasattr(term_color, str_color):
            @colorize(term_color.__dict__[str_color])
            def iter_func(self):
                return self.text
            return iter_func(self)

        raise Exception("Suppose there is no valid attribute")

def generate_color_function(str_method):
    if hasattr(term_color, str_method):
        @colorize(term_color.__dict__[str_method])
        def iter_func(self):
             return self.text
        setattr(Color, "as_" + str_method, iter_func)

# For each "color" from term_color create function "as_color" to represent a special color for string
[generate_color_function(nMethod) for nMethod in dir(term_color) if not nMethod.startswith("__") and not nMethod == "reset"]