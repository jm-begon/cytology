# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 12:27:01 2014

@author: Jm Begon
"""

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

from abc import ABCMeta, abstractmethod
from tile import Tile
try:
    import Image
except ImportError:
    from PIL import Image
import numpy as np


class TileStream:
    """
    ===========
    TileStream
    ===========
    An :class:`TileStream` is a stream of tiles belonging to the same image.
    The tiles may be loaded on request and may overlap.
    """
    __metaclass__ = ABCMeta

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    @abstractmethod
    def next(self):
        pass


class UniqueTileStream(TileStream):
    """
    ================
    UniqueTileStream
    ================
    A :class:`UniqueTileStream` is a stream which returns a single tile

    Constructor parameters
    ----------------------
    tile_loader : TileLoader
        the object which loads the tile
    seed : TileLoader dependant
            A seed to load the image
    """
    def __init__(self, tile_loader, seed):
        self.loader = tile_loader
        self.seed = seed

    def next(self):
        return self.loader.load(self.seed)


class TileStreamBuilder:
    """
    =================
    TileStreamBuilder
    =================
    An abstract base class for builder which produces :class:`TileStream`
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def build(self, tile_loader, seed):
        """
        Builds a :class:`TileStream`.

        Parameters
        ----------
        tile_loader : TileLoader
            the object which loads the tile
        seed : TileLoader dependant
            A seed to load the image
        """
        pass

    def __call__(self, tile_loader, seed):
        """
        Builds a :class:`TileStream`.

        Parameters
        ----------
        tile_loader : TileLoader
            the object which loads the tile
        seed : TileLoader dependant
            A seed to load the image
        """
        return self.build(tile_loader, seed)


class UniqueTileStreamBuilder(TileStreamBuilder):
    """
    =======================
    UniqueTileStreamBuilder
    =======================
    A builder for :class:`UniqueTileStream`
    """
    def build(self, tile_loader, seed):
        return UniqueTileStream(tile_loader, seed)


class TileLoader:
    """
    ===========
    TileLoader
    ===========
    A class which can "load" tiles

    Constructor parameters
    ----------------------
    image_converter : ImageConverter
        A converter to get the appropriate format
    """

    __metaclass__ = ABCMeta

    def __init__(self, image_converter):
        self.converter = image_converter

    @abstractmethod
    def _load(self, seed=None):
        """
        Load an image based on the seed. The tile wrapper is constructed
        in the :method:`load` method.

        Parameters
        ----------
        seed : TileLoader dependant (default : None)
            A seed to load the image

        Return
        ------
        image : TileLoader dependant
            The corresponding image
        """
        pass

    def load(self, seed=None):
        """
        Load a tile based on the seed. The tile has a easting and northing
        of 0. It must be reimplimented if this is not the expected behavior.

        Parameters
        ----------
        seed : TileLoader dependant (default : None)
            A seed to load the image

        Return
        ------
        tile : TileLoader dependant
            The corresponding tile
        """
        tile = Tile(self._load(seed))
        tile.patch = self.converter.convert(tile.patch)
        return tile


class PILLoader(TileLoader):
    """
    =========
    PILLoader
    =========
    A class which can load image files into :class:`PIL.Image`.
    See the PIL library for more information.
    """
    def __init__(self, image_converter):
        TileLoader.__init__(self, image_converter)

    def _load(self, image_file):
        """
        Load a tile from a file

        Parameters
        ----------
        image_file : str or file
            The path to the file

        Return
        ------
        tile : PIL.Image
            The corresponding image
        """
        return Tile(Image.open(image_file))


class NotCMapPILLoader(PILLoader):
    """
    ==================
    NotCMapTileLoader
    ==================
    Load image file and convert palette into RGB if necessary
    """
    def __init__(self, image_converter):
        PILLoader.__init__(self, image_converter)

    def _load(self, image_file):
        image = Image.open(image_file)

        if image.mode == "P":
            image = image.convert("RGB")
        return Tile(image)


class NumpyLoader(TileLoader):
    """
    ===========
    NumpyLoader
    ===========
    Load a numpy file representing an image
    """
    def __init__(self, image_converter):
        TileLoader.__init__(self, image_converter)

    def _load(self, numpy_file):
        """
        Load a image from a file

        Parameters
        ----------
        numpy_file : str or file
            The path to the file

        Return
        ------
        image : numpy array representing an image
            The corresponding image
        """
        return Tile(np.load(numpy_file))
