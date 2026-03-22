#!/usr/bin/env python3
"""Sync version from package.json → src/gslide/__init__.py"""
import json, re, pathlib

v = json.load(open("package.json"))["version"]
p = pathlib.Path("src/gslide/__init__.py")
p.write_text(re.sub(r'__version__ = "[^"]*"', f'__version__ = "{v}"', p.read_text()))
print(f"Synced __version__ = \"{v}\"")
