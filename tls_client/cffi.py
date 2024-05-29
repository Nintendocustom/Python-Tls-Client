import ctypes
import os
from platform import machine
from sys import platform

if platform == 'darwin':
    file_ext = '-arm64.dylib' if machine() == "arm64" else '-x86.dylib'
elif platform in ('win32', 'cygwin'):
    file_ext = '-64.dll' if 8 == ctypes.sizeof(ctypes.c_voidp) else '-32.dll'
else:
    if machine() == "aarch64":
        file_ext = '-arm64.so'
    elif "x86" in machine():
        file_ext = '-x86.so'
    else:
        file_ext = '-amd64.so'

root_dir = os.path.abspath(os.path.dirname(__file__))
library = ctypes.cdll.LoadLibrary(f'{root_dir}/dependencies/tls-client{file_ext}')

# https://bogdanfinn.gitbook.io/open-source-oasis/shared-library/exposed-methods
# extract the exposed request function from the shared package
request = library.request
request.argtypes = [ctypes.c_char_p]
request.restype = ctypes.c_char_p

getCookiesFromSession = library.getCookiesFromSession
getCookiesFromSession.argtypes = [ctypes.c_char_p]
getCookiesFromSession.restype = ctypes.c_char_p

addCookiesToSession = library.addCookiesToSession
addCookiesToSession.argtypes = [ctypes.c_char_p]
addCookiesToSession.restype = ctypes.c_char_p

freeMemory = library.freeMemory
freeMemory.argtypes = [ctypes.c_char_p]
freeMemory.restype = ctypes.c_char_p

destroySession = library.destroySession
destroySession.argtypes = [ctypes.c_char_p]
destroySession.restype = ctypes.c_char_p

destroyAll = library.destroyAll
destroyAll.restype = ctypes.c_char_p
