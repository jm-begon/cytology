# -*- coding: utf-8 -*-
"""
Created on Tue Sep 09 09:59:17 2014

@author: Jm Begon
"""

from shapely import union


def merge_on_intersect(geometry1, geometry2):
    if geometry1.intersect(geometry2):
        return union(geometry1, geometry2)
    return None


def _union(current_tile, border_geometries, neighbor_tile):
    if not neighbor_tile:
        return

    for index in border_geometries:
        local_geometry = current_tile.get(index)
        for index2 in neighbor_tile:
            neighbor_geometry = neighbor_tile.get(index2)
            new_geometry = merge_on_intersect(local_geometry,
                                              neighbor_geometry)
            if new_geometry:
                current_tile.set(index, new_geometry)
                neighbor_tile.set(index2, new_geometry, False)


def merge_annotations(tile_mapper):
    for tile in tile_mapper:

        #East
        border_geometries = tile.east
        neighbor_tile = tile._east_tile
        _union(tile, border_geometries, neighbor_tile)

        #South East
        border_geometries = tile.southeast
        neighbor_tile = tile._southeast_tile
        _union(tile, border_geometries, neighbor_tile)

        #South
        border_geometries = tile.south
        neighbor_tile = tile._south_tile
        _union(tile, border_geometries, neighbor_tile)

        #South West
        border_geometries = tile.southwest
        neighbor_tile = tile._southwest_tile
        _union(tile, border_geometries, neighbor_tile)


class TileEntry:

    def __init__(self, geometry):
        self.geometry = geometry
        self.pattern = True

    def setGeometry(self, geometry, pattern=True):
        self.geometry = geometry
        self.pattern = pattern


class Tile:

    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._north_tile = None
        self._south_tile = None
        self._west_tile = None
        self._east_tile = None
        self._northeast_tile = None
        self._southwest_tile = None
        self._northwest_tile = None
        self._southeast_tile = None
        self.entries = []
        self.north = []
        self.northeast = []
        self.east = []
        self.southeast = []
        self.south = []
        self.southwest = []
        self.west = []

    def __repr__(self):
        return str((self.x, self.y, self.height, self.width))

    def add_geometry(self, geometry):
        minx, miny, maxx, maxy = geometry.bounds
        touches_north = False
        touches_east = False
        touches_west = False
        touches_south = False

        if minx <= self.x:
            touches_west = True
        if miny <= self.y:
            touches_north = True
        if maxx >= (self.x + self.width):
            touches_east = True
        if maxy >= (self.y + self.height):
            touches_south = True

        gid = len(self.entries)

        if touches_north:
            self.north.append(gid)
            if touches_east:
                self.northeast.append(gid)
            if touches_west:
                self.northwest.append(gid)
        if touches_east:
            self.east.append(gid)
        if touches_south:
            self.south.append(gid)
            if touches_east:
                self.southeast.append(gid)
            if touches_west:
                self.southwest.append(gid)
        if touches_west:
            self.west.append(gid)

        self.entries.append(TileEntry(geometry, touches_north, touches_east,
                                      touches_south, touches_west))

    def get(self, index):
        return self.entries[index].geometry

    def setGeometry(self, index, geometry, pattern=True):
        self.entries[index].setGeometry(geometry, pattern)


class TileMapper:

    def __init__(self, zone_height, zone_width, tile_height, tile_width):
        self.height = zone_height
        self.width = zone_width
        self.tile_height = tile_height
        self.tile_wdith = tile_width

        # Dividing the space
        nb_columns = zone_width // tile_width
        extra_column_size = zone_width - (nb_columns*tile_width)
        if extra_column_size > 0:
            nb_columns += 1

        nb_rows = zone_height // tile_height
        extra_row_size = zone_height - (nb_rows*tile_height)
        if extra_row_size > 0:
            nb_rows += 1

        self.nb_rows = nb_rows
        self.nb_cols = nb_columns
        self.nb_tiles = nb_rows * nb_columns

        # Creating the tiles
        self.tiles = [[None for x in xrange(nb_columns)]
                      for x in xrange(nb_rows)]
        for row in xrange(nb_rows):
            for col in xrange(nb_columns):
                current_tile_width = tile_width
                current_tile_height = tile_height
                # Adaptation for extra row/column
                if extra_row_size > 0 and row == (nb_rows - 1):
                    current_tile_height = extra_row_size
                if extra_column_size > 0 and col == (nb_columns - 1):
                    current_tile_width = extra_column_size
                top_left_x = tile_width * col
                top_left_y = tile_height * row

                current_tile = Tile(top_left_x, top_left_y,
                                    current_tile_height, current_tile_width)
                self.tiles[row][col] = current_tile

        # Adding the topology
        for row in xrange(nb_rows):
            for col in xrange(nb_columns):
                if row > 0:
                    self.tiles[row][col]._north_tile = self.tiles[row-1][col]
                if row < nb_rows - 1:
                    self.tiles[row][col]._south_tile = self.tiles[row+1][col]
                if col > 0:
                    self.tiles[row][col]._west_tile = self.tiles[row][col-1]
                if col < nb_columns - 1:
                    self.tiles[row][col]._east_tile = self.tiles[row][col+1]

    def first_tile(self):
        return self.tiles[0][0]

    def __iter__(self):
        return RowOrderIterator(self)

    def get(self, row, column):
        return self.tiles[row][column]


class RowOrderIterator:

    def __init__(self, tile_mapper):
        self.tile_mapper = tile_mapper
        self.col = -1
        self.row = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        self.col += 1
        if self.col >= self.tile_mapper.nb_cols:
            self.col = 0
            self.row += 1
        if self.row >= self.tile_mapper.nb_rows:
            raise StopIteration()
        return self.tile_mapper.get(self.row, self.col)



#TODO REMOVE--------------------------v---------------

class Polygon:
    def __init__(self, *args):
        self.pts = []
        minx = 1000
        miny = 1000
        maxx = 0
        maxy = 0
        for points in args:
            self.pts.append(points)
            x, y = points
            if x < minx:minx = x
            if x > maxx:maxx = x
            if y < miny:miny = y
            if y > maxy:maxy = y
        self.bounds = (minx, miny, maxx, maxy)

    def __repr__(self):
        return str(self.pts)

def test(tile):
    print "geom : ", tile.geometries
    print "North : ", tile.north_border_geometries
    print "South : ", tile.south_border_geometries
    print "East : ", tile.east_border_geometries
    print "Wesst : ", tile.west_border_geometries