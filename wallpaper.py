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

    # The user has 2 basic theme options under Gnome: Default and Dark.
    # To get a valid wallpaper image path, we must first figure out
    # which theme the user has active.
    #
    # The string `'default'` is returned when the Default theme is active.
    # For the Dark theme, `'prefer-dark'` is returned.
    stdout = sp.run(
        'gsettings get org.gnome.desktop.interface color-scheme',
        capture_output=True,
        shell=True,
        universal_newlines=True
    ).stdout.strip().replace("'", '')

    # Note that both `picture-uri` and `picture-uri-dark` will
    # return a value regardles of the user's theme. We have to figure out,
    # for our purposes, which one is valid and which one is bogus.
    picture_uri = 'picture-uri-dark' if stdout == 'prefer-dark' else 'picture-uri'
    try:
        stdout = sp.run(
            f'gsettings get org.gnome.desktop.background {picture_uri}',
            capture_output=True,
            shell=True,
            universal_newlines=True
        ).stdout.strip().replace("'", '')
        return stdout.removeprefix('file://')
    except Exception:
        raise RuntimeError('Could not find wallpaper in Gnome')

def _impl_winblows() -> Text:
    # check if 7, 10, etc
    raise NotImplementedError('Not implemented for Windows (yet?)')
