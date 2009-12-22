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


#ifndef GAMECONTEXT_H
#define GAMECONTEXT_H

#include "tiles.h"

typedef struct GameContext GameContext;

struct GameContext {
	int turns;
	int wall_size;
	int open_sets_count;
	int round_wind;
	int player_wind;
	TileSet open_sets[4];
	tile_id wall[TILES_COUNT];
	tile_id hand[TILES_COUNT];
};

void init_gamecontext(GameContext *gc);

#endif // GAMECONTEXT_H
