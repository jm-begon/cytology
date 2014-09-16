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

from imageconverter import NumpyConverter, PILConverter, CVConverter


class Tile:
    """
    ====
    Tile
    ====

    A :class:`Tile` instance is a patch of a larger image. It uses two
    coordinate systems (in image convention). The tile coordinates refer
    to the relative position of an object to the upper left corner of the tile.
    The image coordinates refer to the absolute location of an object with
    respect to the whole enclosing image.

    Attributes
    ----------
    patch :
        The image patch to store
    easting : int
        The column offset of this Tile
    northing : int
        The row offset ot this Tile

    Constructor parameters
    ----------------------
    patch :
        The image patch to store
    easting : int (default : 0)
        The column offset of this Tile
    northing : int (default : 0)
        The row offset ot this Tile
    """

    def __init__(self, patch, easting=0, northing=0):
        self.easting = easting
        self.northing = northing
        self.patch = patch

    def image_coordinate(self, row=0, col=0):
        """
        Translates tile coordinates to image coordinates

        Parameters
        ----------
        row : int (default : 0)
            The row (in tile coordinates) of pixel to translate in image
            coordinates
        column : int (default : 0)
            The column (in tile coordinates) of pixel to translate in image
            coordinates

        Return
        ------
        pixel_coordinates = (row, col)
            row : int
                The row index in image coordinates
            col : int
                The column index in image coordinates
        """
        return row + self.northing, col + self.easting

    def patch_as_numpy(self):
        """
        Return
        ------
        patch : numpy.ndarray
            The pacth in numpy.ndarray format
        """
        converter = NumpyConverter()
        return converter.convert(self.patch)

    def patch_as_PIL(self):
        """
        Return
        ------
        patch : PIL.Image
            The pacth in PIL.Image format
        """
        converter = PILConverter()
        return converter.convert(self.patch)

    def patch_as_cv(self):
        """
        Return
        ------
        patch : openCV style
            The pacth in openCV format
        """
        converter = CVConverter()
        return converter.convert(self.patch)
