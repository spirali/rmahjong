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


#ifndef EVAL_H
#define EVAL_H

#include "tiles.h"
#include "gamecontext.h"

typedef struct SearchContext SearchContext;

struct SearchContext {
	int pair;
	TileSet *sets[4];
	GameContext gc;
	double best_value;

	#ifdef DEBUG
	double best_prob;
	int best_score;
	TileSet *best_sets[4];
	#endif

	tile_id best_target[TILES_COUNT];
};



void init_tiles(int *tiles, int count, tile_id *out);
int tiles_count(tile_id *tile);
float probability_of_get_missing(tile_id *tile, tile_id *wall, int wall_size, int turns);
int compute_yaku_of_hand(tile_id *hand, TileSet *open_sets, int open_sets_count, int round_wind, int player_wind);
int drop_candidates(GameContext *gc, tile_id *candidates);

void find_best(SearchContext *context, TileSet *sets);
int choose_drop_tile(GameContext *gc);
int steal_chance(GameContext *gc, TileSet *sets, int sets_count, int tile);


#endif // EVAL_H
