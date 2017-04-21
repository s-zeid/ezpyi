from __future__ import print_function


import optparse
import os
import sys

from . import PYINSTALLER_PATH, PYTHON_PATH, WINDOWS
from . import ezpyi


def main(argv=None):
 if not argv:
  argv = sys.argv
 
 prog = argv[0] or "ezpyi"
 usage = "Usage: %s [options] script [exefile]" % os.path.basename(prog)
 p = optparse.OptionParser(prog=prog, usage=usage,
  description="Makes a standalone executable from a Python script using"
              " PyInstaller.")
 p.add_option("--ezpyi-version", action="store_true",
  help="show ezpyi's version number and exit")
 p.add_option("--django", "-D", action="store_true", default=False,
  help="the script represents a Django app.  Defaults to False.")
 p.add_option("--icon", "-i", default=None,
  help="icon to use for the EXE file.  Can be either filename.ico or"
       " filename.exe,index.  (Windows only)")
 p.add_option("--output", "-o", default=None, 
  help="directory to save the resulting file to.  Defaults to the current"
       " directory.")
 p.add_option("--pyinstaller-path", "-P", default=None, dest="pyinstaller",
  help="path to PyInstaller.  Defaults to %s." % PYINSTALLER_PATH)
 p.add_option("--python-path", "-p", default=None, dest="python",
  help="path to the Python binary used to run PyInstaller.  Defaults to %s."
        % PYTHON_PATH)
 p.add_option("--real-name", default=None,
  help="the actual name of the script, e.g. if the input file is a temporary"
       "file with a random name.")
 p.add_option("--tk", "-t", action="store_true", default=False,
  help="include TCL/TK in the executable file.")
 p.add_option("--version", "-V", default=None,
  help="version number to use in the EXE file.  (Windows only)")
 p.add_option("--windowed", "-w", action="store_true", default=False,
  help="use the Windows subsystem in the EXE file in order to hide the console"
       " window.  (Windows only)")
 p.add_option("--debug", action="store_true", default=False,
  help="enable PyInstaller's debugging mechanism in the bundled executable.")
 options, args = p.parse_args(argv[1:])
 if len(args) < 1 or len(args) > 2:
  p.print_help()
  return 2
 
 output = options.output or "."
 script = args[0]
 exename = os.path.splitext(script)[0]
 if WINDOWS:
  exename += ".exe"
 exefile = args[1] if len(args) == 2 else exename
 if os.path.isdir(os.path.realpath(exefile)):
  exefile = os.path.join(exefile, exename)
 if ezpyi(script, exefile, options.tk, options.windowed, options.debug,
          options.icon, options.version,
          options.django,
          options.pyinstaller, options.python, options.real_name) == False:
  print("building failed!", file=sys.stderr)
  return 1


if __name__ == "__main__":
 try:
  sys.exit(main(sys.argv))
 except KeyboardInterrupt:
  pass
