
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "io.h"
#include "tiles.h"

#define LINE_LENGTH_LIMIT 4096

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
	char line[LINE_LENGTH_LIMIT];
	char *s = fgets(line, LINE_LENGTH_LIMIT, file);
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

int read_sets(FILE *file, TileSet *set, int max, int *count)
{
	char line[LINE_LENGTH_LIMIT];
	char *s = fgets(line, LINE_LENGTH_LIMIT, file);
	if (s == NULL)
		return 0;

	char *delim = "\n\t\r ";
	char *token = strtok(line, delim);
	int c = 0;
	while(token && c < max) {
		int type;
		if (!strcmp("Chi", token)) {
			type = CHI;
		} else if (!strcmp("Pon", token)) {
			type = PON;
		} else {
			return 0;
		}

		token = strtok(NULL, delim);

		if (token == NULL) {
			return 0;
		}
		int tile = tile_from_name(token);
		if (tile == TILE_NONE) {
			return 0;
		}
		set[c].type = type;
		set[c].tile = tile;
		c++;
		token = strtok(NULL, delim);
	}
	*count = c;
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


