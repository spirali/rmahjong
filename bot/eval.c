
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
			double value = result * score_of_hand(context->gc.hand, context->pair, context->sets);
		//	value = result;

			if (value > context->best_value) {
				context->best_value = value;
				copy_tiles(sets_tiles, context->best_target);
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
	context->sets[free - 1] = set;
	if (set->type != CHI) {
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
		context->sets[3 - t] = &context->gc.open_sets[3 - t];
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
