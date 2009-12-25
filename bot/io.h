/* Copyright (C) 2009 Stanislav Bohm 
 
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with this program; see the file COPYING. If not, see 
  <http://www.gnu.org/licenses/>.
*/


#ifndef IO_H
#define IO_H

#include <stdio.h>
#include "tiles.h"
#include "gamecontext.h"

void dump_tiles(tile_id *tile);
void dump_set(FILE *file, TileSet *set);
int read_tiles(FILE *file, tile_id *out);
int read_wall(FILE *file, tile_id *out);
int read_sets(FILE *file, TileSet *set, int max, int *count);
tile_id * read_tiles_array(FILE *file);
tile_id read_tile(FILE *file);

#endif // IO_H
