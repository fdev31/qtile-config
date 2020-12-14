#!/bin/sh
cd ~/dev/qtile
pacaur -S gobject-introspection
source venv/bin/activate
pip install dbus-python
pip install pygobject
