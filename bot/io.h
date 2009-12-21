#ifndef IO_H
#define IO_H

#include <stdio.h>
#include "tiles.h"
#include "gamecontext.h"

void dump_tiles(tile_id *tile);
int read_tiles(FILE *file, tile_id *out);
int read_wall(FILE *file, tile_id *out);
int read_sets(FILE *file, TileSet *set, int max, int *count);
tile_id * read_tiles_array(FILE *file);
tile_id read_tile(FILE *file);

#endif // IO_H
