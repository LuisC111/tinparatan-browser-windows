#!/usr/bin/env python3
# Copyright 2026 The Tinparatan Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Names for the Windows installer and zip.

package.py and signing.py import this so those upstream scripts only grow a
short hook. The install directory, shortcut, and GUIDs themselves are in
patches/tinparatan/windows/rebrand.patch. PRODUCT_GUID matches app_guid there.
"""

PRODUCT_NAME = 'Tinparatan'
PACKAGE_PREFIX = 'tinparatan'
# Same company path Helium uses, so the profile is imput\Tinparatan.
COMPANY_PATH = 'imput'
# Distinct from Helium {FB68A146-637A-48C2-A0C4-1565DE45FEBD}.
PRODUCT_GUID = '{38C54E82-5F4F-4AC4-A1DF-565207FF57D7}'
HELIUM_PRODUCT_GUID = '{FB68A146-637A-48C2-A0C4-1565DE45FEBD}'

SIGNING_PRODUCT = 'Tinparatan'
SIGNING_HELPER = 'Tinparatan Update Helper'
SIGNING_INSTALLER = 'Tinparatan Installer'
SIGNING_URL = 'https://github.com/LuisC111/tinparatan-browser-windows'

_KINDS = {
    'installer': '-installer.exe',
    'mini-installer': '-mini-installer.exe',
    'zip': '-windows.zip',
}


def nsis_defines():
    """makensis -D flags. helium.nsi keeps Helium as the default without them."""
    return [
        f'-DPRODUCT_NAME={PRODUCT_NAME}',
        f'-DPRODUCT_GUID={PRODUCT_GUID}',
    ]


def artifact_name(version, target_cpu, kind):
    """File name under build/, for example tinparatan_0.20.2.1_x64-installer.exe."""
    try:
        suffix = _KINDS[kind]
    except KeyError as exc:
        raise ValueError(f'unknown package kind {kind}') from exc
    return f'{PACKAGE_PREFIX}_{version}_{target_cpu}{suffix}'


def _self_check():
    """Fail if the published names drift back to Helium's."""
    assert PRODUCT_GUID != HELIUM_PRODUCT_GUID
    assert not PRODUCT_GUID.startswith('{FB68')
    name = artifact_name('0.20.2.1', 'x64', 'installer')
    assert name == 'tinparatan_0.20.2.1_x64-installer.exe', name
    assert artifact_name('0.20.2.1', 'arm64', 'zip').startswith('tinparatan_')
    assert all(item.startswith('-DPRODUCT_') for item in nsis_defines())
    assert 'helium_' not in name


if __name__ == '__main__':
    _self_check()
    print('tinparatan packaging names ok')
