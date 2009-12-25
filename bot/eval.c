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


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tools.h"
#include "eval.h"
#include "score.h"
#include "io.h"

static double good_combinations_count(tile_id *tile, int ti, int used, double mul, double sum, tile_id *wall, int others,  int turns)
{
	if (ti >= TILES_COUNT) {
		if (used > turns) {
			return sum;
		} else {
			return sum + mul * combinations_d(others, turns - used);
		}
	}
	int wc = wall[ti];
	int count = tile[ti];

	if (count == 0) {
		return good_combinations_count(tile, ti + 1, used, mul, sum, wall, others, turns);
	}

	if (wc < count) {
		return 0;
	}

	int t;
	for (t=count; t <= wc; t++) {
		sum = good_combinations_count(tile, ti + 1, used + t, mul * combinations(wc, t), sum, wall, others, turns);
	}
	return sum;
}


float probability_of_get_missing(tile_id *tile, tile_id *wall, int wall_size, int turns)
{
	int others = wall_size;
	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		if (tile[t] > 0) { others -= wall[t]; }
	}
	if (others < 0)
		return 0.0;
	double gc = good_combinations_count(tile, 0, 0, 1, 0, wall, others, turns);

	return ((double) gc) / combinations_d(wall_size, turns);
}

static int find_missing_tiles(tile_id *hand, tile_id *target, tile_id *missing)
{
	int t;
	int sum = 0;
	for (t = 0; t < TILES_COUNT; t++) {
		int d = target[t] - hand[t];
		if (d > 0) {
			missing[t] = d;
			sum += d;
		} else {
			missing[t] = 0;
		}
	}
	return sum;
}

static void copy_tiles(tile_id *src, tile_id *dest)
{
	memcpy(dest, src, sizeof(tile_id) * TILES_COUNT);
}

void check_sets(SearchContext *context, tile_id *sets_tiles)
{
	tile_id missing[TILES_COUNT];
	int mcount = find_missing_tiles(context->gc.hand, sets_tiles, missing);

	if (mcount > 6) {
		return;
	}

	if (mcount == 0) {
		return;
	}

	int others = context->gc.wall_size;
	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		if (missing[t] > 0) { others -= context->gc.wall[t]; }
	}

	if (others >= 0) {
		double gc = good_combinations_count(missing, 0, 0, 1, 0, context->gc.wall, others, context->gc.turns);
		if (gc > 0) {
			double result = gc / combinations_d(context->gc.wall_size, context->gc.turns);
			int score = score_of_hand(context->gc.hand, context->pair, context->sets, context->gc.open_sets_count, context->gc.round_wind, context->gc.player_wind);
			double value = result * score;
		//	value = result;

			if (value > context->best_value) {
				context->best_value = value;
				copy_tiles(sets_tiles, context->best_target);
				
				#ifdef DEBUG
				context->best_score = score;
				context->best_prob = result;
				context->best_sets[0] = context->sets[0];
				context->best_sets[1] = context->sets[1];
				context->best_sets[2] = context->sets[2];
				context->best_sets[3] = context->sets[3];
				#endif
				//dump_tiles(context->best_target);
				//printf("New b %lf %lf %i\n", result, value,  score_of_hand(context->gc.hand, context->pair, context->sets));
			}
		}
	}
	
}

/* set - remaining sets
   free - how many sets we have to select to get 4 sets */
void compute_best(TileSet *set, int free, tile_id *sets_tiles, SearchContext *context)
{
	if (free == 0) {
		check_sets(context, sets_tiles);
		return;
	}

	if (set->type == INVALID_SET) {
		return;
	}

	compute_best(set + 1, free, sets_tiles, context);
	if (set->type != CHI) {
		context->sets[free - 1] = set;
		if (context->pair == set->tile) {
			return;
		}

		sets_tiles[set->tile] += 3;
		compute_best(set + 1, free - 1, sets_tiles, context);
		sets_tiles[set->tile] -= 3;
	} else {
		int t;
		int tl = set->tile;
		for (t=1; t <= free; t++) {
			context->sets[free - t] = set;
			sets_tiles[tl]++;
			sets_tiles[tl + 1]++;
			sets_tiles[tl + 2]++;
			compute_best(set + 1, free - t, sets_tiles, context);
		}

		sets_tiles[tl]-=free;
		sets_tiles[tl + 1]-=free;
		sets_tiles[tl + 2]-=free;
	}
}

void find_best(SearchContext *context, TileSet *all_sets) 
{
	int t;
	tile_id sets_tiles[TILES_COUNT];
	zero_tiles(sets_tiles);
	context->best_value = 0;
	zero_tiles(context->best_target);

	for (t = 0; t < context->gc.open_sets_count; t++)  {
		context->sets[3 - t] = &context->gc.open_sets[t];
	}

	for (t = 0; t < TILES_COUNT; t ++) {
		context->pair = t;
		sets_tiles[t] += 2;
		compute_best(all_sets, 4 - context->gc.open_sets_count, sets_tiles, context);
		sets_tiles[t] -= 2;
	}
}

int unnecessary_tiles(tile_id *hand, tile_id *target, tile_id *out)
{
	int t;
	int count = 0;
	for (t = 0; t < TILES_COUNT; t++)
	{
		int d = hand[t] - target[t];
		out[t] = d > 0?d:0;
		count += out[t];
	}
	return count;
}

int pick_tile(tile_id *tiles, int id)
{
	int v = 0;
	int t = 0;
	do {
		v += tiles[t++];
	} while(v <= id);
	return t - 1;
}

TileSet * all_tilesets_for_hand(tile_id *hand)
{
	TileSet *sets = malloc(sizeof(TileSet) * (SETS_COUNT + 1));

	int t;
	int pos = 0;
	for (t = 0; t < TILES_COUNT; t++) {
		if (hand[t] > 0) {
			sets[pos].type = PON;
			sets[pos].tile = t;
			pos++;
		}
	}

	for (t = 0; t < 7; t++) {
		sets[pos].type = CHI;
		sets[pos].tile = TILE_B1 + t;
		pos++;
		sets[pos].type = CHI;
		sets[pos].tile = TILE_P1 + t;
		pos++;
		sets[pos].type = CHI;
		sets[pos].tile = TILE_C1 + t;
		pos++;
	}
	sets[pos].type = INVALID_SET;
	return sets;
}


int choose_drop_tile(GameContext *gc)
{
	SearchContext context;
	context.gc = *gc;
	TileSet *all = all_tilesets_for_hand(gc->hand);
	find_best(&context, all);
	free(all);

	tile_id unn[TILES_COUNT];
	int unn_count = unnecessary_tiles(gc->hand, context.best_target, unn);
	
	int id = rand() % unn_count;
	return pick_tile(unn, id);
}

int detect_sets(tile_id *hand, tile_id *original_hand, int pair,  TileSet **sets, int set_id, int h, int open_sets_count, int round_wind, int player_wind)
{
	if (set_id >= 4) {
		return count_of_fan(original_hand, pair, sets, open_sets_count, round_wind, player_wind);
	}
	
	if (hand[h] == 0) {
		return detect_sets(hand, original_hand, pair, sets, set_id, h + 1, open_sets_count, round_wind, player_wind);
	}

	if (hand[h] >= 3) {
		TileSet set;
		set.tile = h;
		set.type = PON;
		sets[set_id] = &set;

		hand[h] -= 3;
		int r = detect_sets(hand, original_hand, pair, sets, set_id + 1, h, open_sets_count, round_wind, player_wind);
		hand[h] += 3;
		if (r > 0)
			return r;
	}

	if (IS_CHI_INDICATOR(h)) {
		if (hand[h + 1] == 0 || hand[h + 2] == 0)
			return 0;

		TileSet set;
		set.tile = h;
		set.type = CHI;
		sets[set_id] = &set;

		hand[h]--;
		hand[h + 1]--;
		hand[h + 2]--;
		int r = detect_sets(hand, original_hand, pair, sets, set_id + 1, h, open_sets_count, round_wind, player_wind);
		hand[h]++;
		hand[h + 1]++;
		hand[h + 2]++;
		return r;
	}

	return 0;
}

int compute_yaku_of_hand(tile_id *hand, TileSet *open_sets, int open_sets_count, int round_wind, int player_wind)
{
	tile_id h[TILES_COUNT];
	copy_tiles(hand, h);
	int t;

	TileSet *sets[4];
	
	for (t = 0; t < open_sets_count; t++) {
		sets[t] = &open_sets[t];
	}

	for (t = 0; t < TILES_COUNT; t++) {
		if (h[t] >= 2) {
			h[t] -= 2;
			int r = detect_sets(h, hand, t, sets, open_sets_count, 0, open_sets_count, round_wind, player_wind);
			h[t] += 2;
			if (r) {
				return r;
			}
		}
	}
	return 0;
}

int steal_chance(GameContext *gc, TileSet *sets, int sets_count, int tile)
{
	SearchContext context;
	context.gc = *gc;
	TileSet *all = all_tilesets_for_hand(gc->hand);
	find_best(&context, all);

	double best_value = context.best_value;
	int best_choice = -1;

	int t;
	context.gc.open_sets_count++;
	context.gc.hand[tile]++;
	for(t=0; t < sets_count; t++) {
		context.gc.open_sets[context.gc.open_sets_count - 1] = sets[t];
		remove_set_from_tiles(context.gc.hand, &sets[t]);
		find_best(&context, all);
		add_set_to_tiles(context.gc.hand, &sets[t]);
		if (best_value < context.best_value) {
			best_value = context.best_value;
			best_choice = t;
		}
	}
	context.gc.open_sets_count--;
	context.gc.hand[tile]--;
	free(all);
	return best_choice;
}
