# -*- coding: utf-8 -*-
"""
Copyright 2010-2013 University of Liège, Belgium.

This software is provided 'as-is', without any express or implied warranty.
In no event will the authors be held liable for any damages arising from the
use of this software.

Permission is only granted to use this software for non-commercial purposes.
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "Copyright 2010-2013 University of Liège, Belgium"
__version__ = '0.1'

from tilestream import TileStream, TileLoader, TileStreamBuilder
from tile import Tile


#TODO manage connexion errors
#TODO make something for annotations and their tiles
#TODO allow for storage on disk (maybe not for the reader class)
class CytomineTileLoader(TileLoader):
    """
    ==================
    CytomineTileLoader
    ==================
    Adaptator to the :class:`TileLoader` interface for the Cytomine client

    The seed must an instance of :class:`Reader`
    """
    def __init__(self, image_converter):
        TileLoader.__init__(self, image_converter)

    def _load(self, seed):
        reader = seed
        return reader.data

    def load(self, seed):
        reader = seed
        image = self._load(reader)
        x, y, width, height = reader.window_position
        return Tile(image, x, y)


class CytomineTileStream(TileStream):
    """
    ==================
    CytomineTileStream
    ==================
    Adaptator to the :class:`TileStream` interface for the Cytomine client

    The seed must an instance of :class:`Reader`
    """

    def __init__(self, tile_loader, seed):
        self.reader = seed
        self.loader = tile_loader

    def next(self):
        if not self.reader.next():
            raise StopIteration
        return self.loader.load(self.reader)


class CytomineTileStreamBuilder(TileStreamBuilder):
    """
    ==================
    CytomineTileStreamBuilder
    ==================
    Adaptator to the :class:`TileStreamBuilder` interface for the Cytomine
    client

    The seed must an instance of :class:`Reader`
    """

    def build(self, tile_loader, seed):
        return CytomineTileStream(tile_loader, seed)
