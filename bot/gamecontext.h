#ifndef GAMECONTEXT_H
#define GAMECONTEXT_H

#include "tiles.h"

typedef struct GameContext GameContext;

struct GameContext {
	int turns;
	int wall_size;
	int open_sets_count;
	TileSet open_sets[4];
	tile_id wall[TILES_COUNT];
	tile_id hand[TILES_COUNT];
};

void init_gamecontext(GameContext *gc);

#endif // GAMECONTEXT_H
