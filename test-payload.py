import os
import sys

import __hello__


def out(k, v):
 print("%s = %r" % (k, v))


print()
out("sys.version", sys.version)
out("__name__", __name__)
out("$ARGV0", os.environ.get("ARGV0", None))
out("sys.argv", sys.argv)
