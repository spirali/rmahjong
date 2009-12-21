#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include "tools.h"
#include "eval.h"
#include "tiles.h"
#include "score.h"
#include "io.h"

void init() {
	srandom(time(0));
}

void process_commands(FILE *file, FILE *fileout, GameContext *gc)
{
	for(;;) {
		fflush(fileout);
		char line[4096];
		if (fgets(line, 4096, file) == NULL)
			break;

		if (line[0] == '#') {
			continue;
		}

		int l = strlen(line);
		while (line[l - 1]  == '\n' || line[l - 1] == '\r') { 
			l--;
			line[l] = 0;
		}

		// printf(">> %s\n", line);

		if (!strcmp(line, "QUIT")) {
			break;
		}
		
		if (!strcmp(line, "WALL")) {
			if (!read_tiles(file, gc->wall)) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			} else {
				gc->wall_size = tiles_count(gc->wall);
			}
			continue;
		}

		if (!strcmp(line, "HAND")) {
			if (!read_tiles(file, gc->hand)) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}	
			continue;
		}

		if (!strcmp(line, "DISCARD")) {
			int tile = choose_drop_tile(gc);
			fprintf(fileout, "%s\n", tile_name[tile]);
			continue;
		}

		if (!strcmp(line, "TURNS")) {
			if (fscanf(file, "%i\n", &gc->turns) != 1) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}
			continue;
		}

		if (!strcmp(line, "SETS")) {
			if (!read_sets(file, gc->open_sets, 4, &gc->open_sets_count)) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}	
			continue;
		}

		if (!strcmp(line, "YAKU")) {
			int yaku = compute_yaku_of_hand(gc->hand, gc->open_sets, gc->open_sets_count, gc->round_wind, gc->player_wind);
			fprintf(fileout, "%i\n", yaku);
			continue;
		}

		if (!strcmp(line, "DORAS")) {
			tile_id *array = read_tiles_array(file);
			if (array == NULL) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
				continue;
			}
			// TODO: Process DORA
			free(array);
			continue;
		}

		if (!strcmp(line, "ROUND_WIND")) {
			gc->round_wind = read_tile(file);
			if (gc->round_wind == TILE_NONE) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}
			continue;
		}

		if (!strcmp(line, "PLAYER_WIND")) {
			gc->player_wind = read_tile(file);
			if (gc->player_wind == TILE_NONE) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}
			continue;
		}

		fprintf(fileout, "Error: Unknown command\n");
	}
}

int main() {
	init();
	GameContext gc;
	init_gamecontext(&gc);
	process_commands(stdin, stdout, &gc);
	return 0;
}
