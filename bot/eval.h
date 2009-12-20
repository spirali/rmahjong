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
	tile_id best_target[TILES_COUNT];
};



void init_tiles(int *tiles, int count, tile_id *out);
int tiles_count(tile_id *tile);
float probability_of_get_missing(tile_id *tile, tile_id *wall, int wall_size, int turns);
int compute_yaku_of_hand(tile_id *hand, TileSet *open_sets, int open_sets_count);

TileSet * all_tilesets();
void find_best(SearchContext *context, TileSet *sets);
int choose_drop_tile(GameContext *gc);

#endif // EVAL_H
