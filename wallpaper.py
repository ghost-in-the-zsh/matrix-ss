import platform as pt
from typing import Text


def get_wallpaper_filepath() -> Text:
    sys = pt.system().lower()
    if sys == 'linux':
        return _impl_gnu_linux()
    elif sys == 'windows':
        return _impl_windows()
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
    # Check the ~/.config/kscreenlockerrc file:
    # ```
    # [Greeter][Wallpaper][org.kde.image][General]
    # Image=/abs-path/to/wallpaper/file.jpg
    # ```
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
    raise NotImplementedError('Not implemented for Gnome (yet?)')

def _impl_windows() -> Text:
    # check if 7, 10, etc
    raise NotImplementedError('Not implemented for Windows (yet?)')
