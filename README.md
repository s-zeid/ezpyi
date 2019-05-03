ezpyi
=====

A wrapper for PyInstaller that simplifies its usage.

Copyright (c) 2019 S. Zeid.  Some rights reserved under the X11 License.

<https://pypi.org/project/ezpyi>  
<https://code.s.zeid.me/ezpyi>

*                        *                        *                        *

Note:  If all you want to do is bundle a single script without writing a
spec file, PyInstaller is now able to do this out-of-the-box.  However,
ezpyi will hide the spec file from you altogether, output a single file
by default, and not output to a `dist` subdirectory by default.  It also
supports making [AppImages][AppImage] and contains some other convenience
options.


Installation
------------

Run `pip3 install ezpyi`.

Alternatively, clone the repository (or download a release tarball)
and run `python3 setup.py install` from within the root directory
(with root privileges).


Usage
-----

    Usage: ezpyi [options] script [exefile]

Without any options, ezpyi will bundle `script` and its Python dependencies
as an executable file called `exefile`.

`-D` or `--onedir` will bundle the script as a directory called `exefile`.
Unlike stock PyInstaller, the executable file within that directory will
always be called `AppRun`.

`-A` or `--appimage` will bundle the script as an [AppImage][AppImage].
This requires [`appimagetool`][appimagetool] to be on your $PATH.  (AppImage
desktop integration and AppStream are not supported by ezpyi.  If you need
these features, use `-D`, modify the output directory, and manually build
the AppImage.)

For other options, run `ezpyi -h`.


[AppImage]: https://github.com/AppImage/AppImageKit
[appimagetool]: https://github.com/AppImage/AppImageKit/releases
