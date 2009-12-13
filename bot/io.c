
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "io.h"
#include "tiles.h"

void dump_tiles(tile_id *tile)
{
	int t;
	printf("{");
	for (t = 0; t < TILES_COUNT; t++) {
		if (tile[t] > 0) {
			printf(" %s:%i,", tile_name[t], tile[t]);
		}
	}
	printf(" }\n");
}

int read_tiles(FILE *file, tile_id *out)
{
	char line[500];
	char *s = fgets(line, 500, file);
	if (s == NULL)
		return 0;

	zero_tiles(out);
	char *delim = "\n\t\r ";
	char *token = strtok(line, delim);
	while(token) {
		int tile = tile_from_name(token);
		if (tile == TILE_NONE) {
			return 0;
		}
		out[tile]++;
		token = strtok(NULL, delim);
	}
	return 1;
}

int read_wall(FILE *file, tile_id *out)
{
	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		int i;
		if (fscanf(file, "%i", &i) != 1) {
			return 0;
		}
		out[t] = i;
	}
	return fscanf(file, "\n") == 0;
}


