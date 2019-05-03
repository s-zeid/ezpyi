from __future__ import print_function


import argparse
import os
import subprocess
import sys

from . import __version__
from . import WINDOWS, PYINSTALLER_PATH, PYTHON_PATH, APPIMAGETOOL_PATH
from . import ezpyi, pyinstaller_script


def main(argv=None):
 if not argv:
  argv = sys.argv
 
 prog = argv[0] or "ezpyi"
 usage = "Usage: %s [options] script [exefile]"
 usage %= os.path.basename(prog)
 p = argparse.ArgumentParser(prog=prog, usage=usage,
  description="Makes a standalone executable from a Python script using"
              " PyInstaller.")
 p.add_argument("--hep", dest="_hep_easter_egg", action="store_true",
                help=argparse.SUPPRESS)
 p.add_argument("--version", "-v", action="store_true",
  help="show ezpyi's version number and exit")
 p.add_argument("--onedir", "-D", action="store_true", default=False,
  help="make an AppImage-compatible directory instead of an executable file"
       " (the executable will be called AppRun, or AppRun.exe on Windows)")
 p.add_argument("--appimage", "-A", action="store_true", default=False,
  help="make an AppImage (appimagetool must be on $PATH;"
       " desktop integration and AppStream are not supported)")
 p.add_argument("--icon", "-i", default=None,
  help="icon to use for the EXE file.  Can be either filename.ico or"
       " filename.exe,index.  (Windows only)")
 p.add_argument("--output-dir", "-O", default=None,
  help="directory to save the resulting file to.  Defaults to the current"
       " directory.")
 p.add_argument("--pyinstaller-path", default=None,
  help="path to PyInstaller.  Defaults to %s." % PYINSTALLER_PATH)
 p.add_argument("--python-path", default=None,
  help="path to the Python binary used to run PyInstaller.  Defaults to %s."
        % PYTHON_PATH)
 p.add_argument("--appimagetool-path", default=None,
  help="path to appimagetool.  Defaults to %s.  Only meaningful on Linux."
        % APPIMAGETOOL_PATH)
 p.add_argument("--real-name", default=None,
  help="the actual name of the script, e.g. if the input file is a temporary"
       " file with a random name.")
 p.add_argument("--exe-version", "-V", default=None,
  help="version number to use in the EXE file.  (Windows only)")
 p.add_argument("--windowed", "-w", action="store_true", default=False,
  help="use the Windows subsystem in the EXE file in order to hide the console"
       " window.  (Windows only)")
 p.add_argument("--django", action="store_true", default=False,
  help="the script represents a Django app.  Defaults to False.")
 p.add_argument("--debug", action="store_true", default=False,
  help="enable PyInstaller's debugging mechanism in the bundled executable.")
 p.add_argument("--makespec-args", "-M", nargs=argparse.REMAINDER, default=None,
  help="pass all remaining arguments to pyi-makespec.  With no remaining"
       " arguments, this will print pyi-makespec's help text and exit.")
 p.add_argument("script", nargs="?", default=None,
  help="the script file to bundle")
 p.add_argument("exename", nargs="?", default=None,
  help="the name of the output file or directory; defaults to the script name"
       " without its file extension")
 
 try:
  options = p.parse_args(argv[1:])
  makespec_want_help = not options.makespec_args and options.makespec_args is not None
  if not (options._hep_easter_egg or options.version or makespec_want_help):
   if options.script is None:
    p.error("the following arguments are required: script")
  if options.output_dir is not None and os.path.isabs(options.exename or ""):
   p.error("--output-dir/-O cannot be used with an absolute path for exename")
 except SystemExit as exc:
  return exc.code
 
 if options._hep_easter_egg:
  print("Hep!  Hep!  I'm covered in sawlder! ... Eh?  Nobody comes.")
  print("--Red Green, https://www.youtube.com/watch?v=qVeQWtVzkAQ#t=6m27s")
  return 0
 
 if options.version:
  print(__version__)
  return 0
 
 if makespec_want_help:
  makespec_cmd = [pyinstaller_script("Makespec", options.pyinstaller_path), "--help"]
  return subprocess.call(makespec_cmd)
 
 output_dir = options.output_dir or "."
 script = options.script
 
 exename = os.path.splitext(os.path.basename(script))[0]
 if WINDOWS:
  exename += ".exe"
 
 exefile = options.exename or exename
 if not os.path.isabs(exefile):
  exefile = os.path.join(output_dir, exefile)
 if os.path.isdir(os.path.realpath(exefile)):
  exefile = os.path.join(exefile, exename)
 
 if ezpyi(script, exefile, options.windowed, options.debug,
          options.icon, options.exe_version,
          options.django,
          options.pyinstaller_path, options.python_path, options.real_name,
          options.onedir, options.appimage, options.appimagetool_path,
          options.makespec_args) == False:
  print("building failed!", file=sys.stderr)
  return 1


if __name__ == "__main__":
 try:
  sys.exit(main(sys.argv))
 except KeyboardInterrupt:
  pass
