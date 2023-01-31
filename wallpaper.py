import platform as pt
from typing import Text


def get_wallpaper_filepath() -> Text:
    sys = pt.system().lower()
    if sys == 'linux':
        return _impl_gnu_linux()
    elif sys == 'windows':
        return _impl_winblows()
    else:
        raise NotImplementedError(f'Not (yet?) implemented for: {sys}')

def _impl_gnu_linux() -> Text:
    from os import environ as env

    kde = ('plasma',)
    gnome = ('ubuntu',)
    session = env['DESKTOP_SESSION']
    if session in kde:
        return _impl_gnu_linux_kde()
    if session in gnome:
        return _impl_gnu_linux_gnome()

    raise NotImplementedError(f'Not implemented for session: {session}')

def _impl_gnu_linux_kde() -> Text:
    # Under the ~/.config/ directory, the following files are of interest:
    #
    #   1. plasma-org.kde.plasma.desktop-appletsrc: Current wallpaper
    #   2. plasmarc: List of manually added wallpapers for the selection screen
    #   3. kscreenlockerrc: The screen lock wallpaper image
    #
    # Format: Image=file:///abs-path/to/wallpaper/file.jpg
    #
    from os.path import join, expanduser

    try:
        path = join(expanduser('~'), '.config', 'plasma-org.kde.plasma.desktop-appletsrc')
        with open(path) as config:
            for line in config.readlines():
                if line.startswith('Image='):
                    return line.split('=')[1].removeprefix('file://').strip()
    except Exception:
        raise RuntimeError('Could not find wallpaper in KDE')

def _impl_gnu_linux_gnome() -> Text:
    import subprocess as sp

    try:
        # The user has 2 basic theme options under Gnome: Default and Dark.
        # To get a valid wallpaper image path, we must first figure out
        # which theme the user has active.
        #
        # The string `'default'` is returned when the Default theme is active.
        # For the Dark theme, `'prefer-dark'` is returned.
        theme = sp.run(
            'gsettings get org.gnome.desktop.interface color-scheme',
            shell=True,
            check=True,
            capture_output=True,
            universal_newlines=True
        ).stdout.strip().replace("'", '')

        # Note that both `picture-uri` and `picture-uri-dark` will
        # return a value regardles of the user's theme. We have to figure out,
        # for our purposes, which one is valid and which one is bogus.
        uri = 'picture-uri-dark' if theme == 'prefer-dark' else 'picture-uri'
        return sp.run(
            f'gsettings get org.gnome.desktop.background {uri}',
            shell=True,
            check=True,
            capture_output=True,
            universal_newlines=True
        ).stdout.strip().removeprefix('file://').replace("'", '')
    except Exception:
        raise RuntimeError('Could not find wallpaper in Gnome')

def _impl_winblows() -> Text:
    import winreg as wr
    # The `winreg` code was tested to work in Windows 7 (Python 3.7) and
    # 10 (Python 3.11). However, there *are* some details to keep in mind:
    #
    #   1. In Win7, when an image is set as the wallpaper, it gets copied over
    #      and renamed; e.g. `QueryValueEx` returned the following tuple:
    #      ('C:\\Users\\<UserName>\\AppData\\Roaming\\Microsoft\\Windows\\Themes\\TranscodedWallpaper.jpg', 1)
    #   2. In Win10, the same tuple as Win7 is returned, but the path
    #      within it MAY NOT BE VALID. What you get is the location where
    #      the image used to be AT THE TIME IT WAS SET by the user as the
    #      wallpaper. By the time we `QueryValueEx`, the image could've been
    #      moved, deleted, renamed, etc. It needs an extra check to verify whether
    #      the file actually exists or not.
    #   3. The following PowerShell command:
    #      PS > Get-ItemPropertyValue \
    #           -Path "Registry::HKEY_CURRENT_USER\Control Panel\Desktop" \
    #           -Name Wallpaper
    #      1. Win7 : Fails. The `Get-ItemPropertyValue` is not recognized, so
    #                it's not implemented there.
    #      2. Win10: Returns the same output as `QueryValueEx`, which probably means
    #                the PowerShell impl. is using `QueryValueEx` under the hood.
    #
    hkey = wr.HKEY_CURRENT_USER
    subkey = 'Control Panel\\Desktop'
    try:
        with wr.OpenKeyEx(hkey, subkey) as regkey:          # type: PyHKEY
            value = wr.QueryValueEx(regkey, 'Wallpaper')    # type: Tuple[str, int]
            path = value[0]
            with open(path): pass   # see Win10 note above
            return path
    except Exception:
        raise RuntimeError('Could not find wallpaper in Windows')
