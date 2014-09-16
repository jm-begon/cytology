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


from dataminer import DataminerCoordinator


def SLDCBuilder():
    pass


class SLDCCoordinator(DataminerCoordinator):
    """
    ===============
    SLDCCoordinator
    ===============
    A :class:`SLDCCoordinator` coordinates a SLDC datamining task :
    Segment : find the intersting part of a image for the task at hand
    Locate : extract coordinates of the intersting part
    Dispatch : sort interesting part in groups based on their characteristics
    Classify : perform fine-grain classification on each group

    Constructor parameters
    ----------------------
    """
    def __init__(self, tile_filter, segmenter, vectorizer, merger_builder,
                 dispatcher, classifier):
        self.filter = tile_filter
        self.segmenter = segmenter
        self.vectorizer = vectorizer
        self.merger_builder = merger_builder
        self.dispatcher = dispatcher
        self.classifier = classifier

    def fit(self):
        pass

    def process(self, image_stream):
        #TODO log the messages
        for tile_stream in image_stream:
            #Get the merger in place
            merger = self.merger_builder.creater_merger()
            for tile in tile_stream:
                #Filtering
                if not self.filter.filter_tile(tile):
                    continue
                #Segmenting
                segmented = self.segmenter.segment(tile)
                #Extracting the polygons
                polygons = self.vectorizer.vectorize(segmented)
                merger.store(tile, polygons)

            #Merging the polygons from different tiles
            merger.merge()







