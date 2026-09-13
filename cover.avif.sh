#!/bin/sh

# TODO set config values
cover_src=0663-level/281.tiff

magick "$cover_src" -scale 50% -quality 50% cover.avif
