python
import sys
sys.path.insert(0, '/home/ilia/Documents/script/gdb/pretty_print/python')
from libstdcxx.v6.printers import register_libstdcxx_printers
register_libstdcxx_printers (None)

from qt4 import register_qt4_printers
register_qt4_printers (None)

end
set auto-solib-add off
sharedlibrary libgdiplusL
sharedlibrary libPalLib
sharedlibrary libPiLib