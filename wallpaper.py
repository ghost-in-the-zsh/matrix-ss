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
    gnome = ('gnome',)
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
    # Check `gconf` for Gnome 2, and `gsettings` for Gnome 3 (and Unity?):
    # ```
    # $ gsettings get org.gnome.desktop.background picture-uri
    # 'file:///usr/share/backgrounds/gnome/adwaita-l.webp'
    # ```
    import subprocess as sp

    try:
        stdout = sp.run(
            # NOTE: If running this from KDE, path will be bogus.
            ['gsettings', 'get', 'org.gnome.desktop.background', 'picture-uri'],
            capture_output=True,
            shell=True,
        ).stdout.strip()
        return stdout.removeprefix('file://')
    except Exception:
        raise RuntimeError('Could not find wallpaper in Gnome')

def _impl_winblows() -> Text:
    # check if 7, 10, etc
    raise NotImplementedError('Not implemented for Windows (yet?)')
