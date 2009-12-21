#include <string.h>

#include "gamecontext.h"

void init_gamecontext(GameContext *gc)
{
	memset(gc, 0, sizeof(GameContext));
	gc->player_wind = TILE_NONE;
	gc->round_wind = TILE_NONE;
}
