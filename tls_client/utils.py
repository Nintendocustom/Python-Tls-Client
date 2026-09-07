from __future__ import annotations

import ctypes
import platform
from typing import Tuple

# (system, arch_key): local filename
dependency_filenames = {
    ('windows', 'amd64'): "tls-client-windows-64.dll",
    ('windows', '386'): "tls-client-windows-32.dll",
    ('darwin', 'arm64'): "tls-client-darwin-arm64.dylib",
    ('darwin', 'amd64'): "tls-client-darwin-amd64.dylib",
    ('linux', 'amd64'): "tls-client-linux-amd64.so",
    ('linux', '386'): "tls-client-linux-386.so",
    ('linux', 'arm64'): "tls-client-linux-arm64.so",
    ('linux', 'arm-7'): "tls-client-linux-arm-7.so",
    ('linux', 'arm-6'): "tls-client-linux-arm-6.so",
    ('linux', 'arm-5'): "tls-client-linux-arm-5.so",
    ('linux', 'riscv64'): "tls-client-linux-riscv64.so",
    ('linux', 'ppc64le'): "tls-client-linux-ppc64le.so",
    ('linux', 's390x'): "tls-client-linux-s390x.so",
}

# (system, arch_key): suffix in the GitHub asset name
upstream_asset_suffixes = {
    ('windows', 'amd64'): "windows-amd64.dll",
    ('windows', '386'): "windows-386.dll",
    ('darwin', 'arm64'): "darwin-arm64.dylib",
    ('darwin', 'amd64'): "darwin-amd64.dylib",
    ('linux', 'amd64'): "linux-amd64.so",
    ('linux', '386'): "linux-386.so",
    ('linux', 'arm64'): "linux-arm64.so",
    ('linux', 'arm-7'): "linux-arm-7.so",
    ('linux', 'arm-6'): "linux-arm-6.so",
    ('linux', 'arm-5'): "linux-arm-5.so",
    ('linux', 'riscv64'): "linux-riscv64.so",
    ('linux', 'ppc64le'): "linux-ppc64le.so",
    ('linux', 's390x'): "linux-s390x.so",
}


def get_system_info() -> Tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == 'darwin':
        return 'darwin', 'arm64' if machine == 'arm64' else 'amd64'

    elif system in ('windows', 'win32', 'cygwin'):
        return 'windows', 'amd64' if ctypes.sizeof(ctypes.c_voidp) == 8 else '386'

    # Assume Linux
    if machine in ('x86_64', 'amd64'):
        arch = 'amd64'
    elif machine in ('i386', 'i686', 'x86'):
        arch = '386'
    elif machine in ('aarch64', 'arm64'):
        arch = 'arm64'
    elif 'armv7' in machine:
        arch = 'arm-7'
    elif 'armv6' in machine:
        arch = 'arm-6'
    elif 'armv5' in machine or machine.startswith('arm'):
        arch = 'arm-5'
    elif 'riscv64' in machine:
        arch = 'riscv64'
    elif 'ppc64le' in machine:
        arch = 'ppc64le'
    elif 's390x' in machine:
        arch = 's390x'
    else:
        # Fallback
        arch = 'amd64'
    return 'linux', arch


def get_dependency_filename() -> str | None:
    system_info = get_system_info()
    return dependency_filenames.get(system_info)


def get_upstream_asset_suffix() -> str | None:
    system_info = get_system_info()
    return upstream_asset_suffixes.get(system_info)
