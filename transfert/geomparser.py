# -*- coding: utf-8 -*-
"""
Created on Tue Sep 09 16:45:04 2014

@author: Jm Begon
"""

from shapely.wkt import loads
from tilemapper import TileMapper, merge_annotations

def parse_file(filepath):
    tile_mapper = TileMapper(104704, 172032, 4096, 4096)
    nb_geom = 0
    with open(filepath, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            tile_info = line.split(" ")
            x = int(tile_info[1])
            y = int(tile_info[2])
            tile = tile_mapper.get_tile_by_corner(x, y)
            nb_geom += int(tile_info[5])
            for index in range(int(tile_info[5])):
                tile.add_geometry(loads(f.readline()))

    print "Nb of geometries (before union) : ", nb_geom
    return tile_mapper


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1]

    tile_mapper = parse_file(filepath)
    merge_annotations(tile_mapper)

    nb_geom = 0
    for tile in tile_mapper:
        for tile_entry in tile.entries:
            if tile_entry.patent:
                nb_geom += 1


    print "Nb of geometries (after union) : ", nb_geom

