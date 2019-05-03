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
 WINDOWS = True
 PYTHON_PATH = "python" #"C:\\Python27\\python.exe"
 PYINSTALLER_PATH = "" #"C:\\Python27\\Scripts"
else:
 WINDOWS = False
 PYTHON_PATH = "python"
 PYINSTALLER_PATH = ""


def ezpyi(infile, outfile, tk=False, windowed=False, debug=False,
          icon=None, version=None,
          django=False,
          pyinstaller_path=None, python_path=None, real_name=None):
 pyinstaller_path = pyinstaller_path or PYINSTALLER_PATH
 python_path = python_path or PYTHON_PATH
 
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
 try:
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
  makespec_cmd = [pyinstaller_script("Makespec", pyinstaller_path), "--onefile"]
  if tk:
   makespec_cmd += ["--tk"]
  if WINDOWS:
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
   #if subprocess.call([pyinstaller_script("Build", pyinstaller_path), spec]) == 0:
   if subprocess.call([pyinstaller_script("", pyinstaller_path), spec]) == 0:
    nametomove = basename + ".exe" if WINDOWS else basename
    shutil.move(os.path.join(tmpdir, "dist", nametomove), outfile)
    ret = True
 finally:
  os.chdir(cwd)
  shutil.rmtree(tmpdir)
 return ret


def _patch_spec(spec, rm_django=True):
 with open(spec, "rb") as f:
  s = f.read()
 excludes = []
 if rm_django:
  excludes += [b"django"]
 #excludes = ", ".join(["'%s'" % i for i in excludes])
 #s = s.replace("pathex=[", "excludes=[" + excludes + "], pathex=[", 1)
 if b"excludes=" not in s:
  s = s.replace(b"pathex=", b"excludes=[], pathex=")
 s = s.replace(b"excludes=None", b"excludes=[]")
 s = s.replace(b"excludes=", b"excludes=[%s]+" % b",".join(b'"%s"'%i for i in excludes))
 with open(spec, "wb") as f:
  f.write(s)


def pyinstaller_script(name=None, pyinstaller_path=PYINSTALLER_PATH):
 script = "pyi-" + name.lower() if name else "pyinstaller"
 return os.path.join(pyinstaller_path, script + (".exe" if WINDOWS else ""))


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
