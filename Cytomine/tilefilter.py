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


from abc import ABCMeta, abstractmethod
import numpy as np


class TileFilter:
    """
    ==========
    TileFilter
    ==========
    A :class:`TileFilter` embeds a predicate which can be applied to tiles
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def filter_tile(self, tile):
        """
        Test whether the tile should be filtered

        Parameters
        ----------
        tile : :class:`Tile`
            The tile to check. The patch may be expected in some specific
            format

        Return
        ------
        success : boolean
            True if the tile passed successfully the test
        """
        pass


class StdFilter:
    """
    =========
    StdFilter
    =========
    A :class:`StdFilter` filters tiles whose color-wise standard deviation
    are below a given threshold.

    Constructor parameters
    ----------------------
    thresholds : int or sequence of ints (default : [10, 10, 10])
        if int
            All color stdev are checked again this single value
        if sequence of ints
            The length of the sequence must match the number of color of
            the processed images. The color stdev are tested again the
            corresponding values
    """
    def __init__(self, thresholds=[10, 10, 10]):
        try:
            if len(thresholds) == 1:
                self.threshold = thresholds[0]
            else:
                self.thresholds = thresholds
        except TypeError:
            self.threshold = thresholds

    def filter_tile(self, tile):
        img = np.asarray(tile.patch)

        if len(img.shape) > 2:
            #Color components
            for i in range(img.shape[2]):
                if img[:, :, i].std() < self.thresholds[i]:
                    return False
            return True

        return img.std() >= self.threshold
