from __future__ import print_function


import optparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


PE_EXTENSIONS = (".cpl", ".dll", ".drv", ".exe", ".ico", ".ocx", ".scr", ".sys")


if platform.system().lower() == "windows":
 windows = True
 python_path = "python" #"C:\\Python27\\python.exe"
 pyinstaller_path = "" #"C:\\Python27\\Scripts"
else:
 windows = False
 python_path = "python"
 pyinstaller_path = ""


def ezpyi(infile, outfile, tk=False, windowed=False, debug=False,
          icon=None, version=None,
          django=False,
          pyinstaller_path=None, python_path=None, real_name=None):
 global windows
 pyinstaller_path = pyinstaller_path or globals()["pyinstaller_path"]
 python_path = python_path or globals()["python_path"]
 infile = real_infile = os.path.abspath(infile)
 outfile = os.path.abspath(outfile)
 basename = os.path.splitext(os.path.basename(infile))[0]
 if real_name is None:
  real_name = infile
 real_basename = os.path.splitext(os.path.basename(real_name))[0]
 is_zip = False
 try:
  z = zipfile.ZipFile(infile, "r")
  is_zip = True
  z.close()
 except zipfile.BadZipfile:
  pass
 cwd = os.getcwd()
 tmpdir = tempfile.mkdtemp()
 os.chdir(tmpdir)
 if is_zip:
  zipdir = tempfile.mkdtemp(dir=tmpdir, prefix="zip-contents-")
  z = zipfile.ZipFile(infile, "r")
  z.extractall(zipdir)
  infile = os.path.join(zipdir, "__main__.py")
  if not os.path.isfile(infile):
   return False
  basename = "__main__"
 spec = os.path.join(tmpdir, basename + ".spec")
 ret = False
 makespec_cmd = [pyinstaller_script("Makespec"), "--onefile"]
 if tk:
  makespec_cmd += ["--tk"]
 if windows:
  if windowed:
   makespec_cmd += ["--windowed"]
  if icon:
   icon_path = icon
   if os.path.splitext(icon.rsplit(",", 1)[0])[1].lower() not in PE_EXTENSIONS:
    icon_path = os.path.join(tmpdir, os.path.basename(icon) + ".ico")
    shutil.copy(icon, icon_path)
   makespec_cmd += ["--icon=" + icon_path]
  if version:
   version_tuple = (re.sub(r'[^0-9.]', '', version).split(".") + [0, 0, 0, 0])[:4]
   version_tuple = tuple([int(i) for i in version_tuple])
   # https://stackoverflow.com/a/14626175
   version_res = """VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={v_tuple},
    prodvers={v_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u''),
        StringStruct(u'FileDescription', u''),
        StringStruct(u'FileVersion', {v_unicode}),
        StringStruct(u'InternalName', {internal_name}),
        StringStruct(u'LegalCopyright', u''),
        StringStruct(u'OriginalFilename', {original_name}),
        StringStruct(u'ProductName', u''),
        StringStruct(u'ProductVersion', {v_unicode})])
      ]), 
  ]
)""".format(v_tuple=repr(version_tuple), v_unicode=repr(to_unicode(version)),
            internal_name=repr(to_unicode(real_basename)),
            original_name=repr(to_unicode(os.path.basename(real_name))))
    #VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
   version_file = os.path.join(tmpdir, "version.txt")
   with open(version_file, "wb") as f:
    f.write(version_res)
   makespec_cmd += ["--version-file="+version_file]
 if debug:
  makespec_cmd += ["--debug"]
 makespec_cmd += ["--specpath="+tmpdir, infile]
 if subprocess.call(makespec_cmd) == 0:
  _patch_spec(spec, rm_django=(not django))
  #if subprocess.call([pyinstaller_script("Build"), spec]) == 0:
  if subprocess.call([pyinstaller_script(), spec]) == 0:
   nametomove = basename + ".exe" if windows else basename
   shutil.move(os.path.join(tmpdir, "dist", nametomove), outfile)
   ret = True
 os.chdir(cwd)
 shutil.rmtree(tmpdir)
 return ret


def _patch_spec(spec, rm_django=True):
 with open(spec, "rb") as f:
  s = f.read()
 excludes = []
 if rm_django:
  excludes += ["django"]
 #excludes = ", ".join(["'%s'" % i for i in excludes])
 #s = s.replace("pathex=[", "excludes=[" + excludes + "], pathex=[", 1)
 if s.find("excludes=") < 0:
  s = s.replace("pathex=", "excludes=[], pathex=")
 s = s.replace("excludes=None", "excludes=[]")
 s = s.replace("excludes=", "excludes=%s+" % repr(excludes))
 with open(spec, "wb") as f:
  f.write(s)


def main(argv):
 global pyinstaller_path, python_path, windows
 prog = "ezpyi"
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
  help="path to PyInstaller.  Defaults to %s." % pyinstaller_path)
 p.add_option("--python-path", "-p", default=None, dest="python",
  help="path to the Python binary used to run PyInstaller.  Defaults to %s."
        % pyinstaller_path)
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
 pyinstaller_path = options.pyinstaller or pyinstaller_path
 python_path = options.python or python_path
 script = args[0]
 exename = os.path.splitext(script)[0]
 if windows:
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


def pyinstaller_script(name=None):
 script = "pyi-" + name.lower() if name else "pyinstaller"
 return os.path.join(pyinstaller_path, script + (".exe" if windows else ""))


if sys.version_info.major < 3:
 def to_unicode(s, encoding="utf8"):
  if isinstance(s, (str, buffer)):
   return unicode(s, encoding)
  elif isinstance(s, unicode):
   return s
  return unicode(s)
else:
 def to_unicode(s, encoding="utf8"):
  if isinstance(s, bytes):
   return s.decode(encoding)
  elif isinstance(s, str):
   return s
  return str(s)
