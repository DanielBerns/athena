# Docs

## how_to_disable_automatic_suspend_on_gdm

1. Log into the gdm user with:

    machinectl shell gdm@ /bin/bash

2. then disable the idle timeout with:

    gsettings set org.gnome.desktop.session idle-delay 0 
