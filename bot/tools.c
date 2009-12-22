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


#include "tools.h"

static int factorial(int x) {
	int v = 1;
	int i;
	for (i = 2; i <= x; i++) {
		v *= i;
	} 
	return v;
}

int combinations(int n, int k) {
	if (n < k) {
		return 0;
	}

	if (n - k < k) {
		k = n - k;
	}

	int s = 1; 
	int i;
	for (i = n - k + 1; i <= n; i++) {
		s *= i;
	}
	return s / factorial(k);
}

static double factorial_d(int x) {
	double v = 1;
	int i;
	for (i = 2; i <= x; i++) {
		v *= i;
	} 
	return v;
}

double combinations_d(int n, int k) {
	if (n < k) {
		return 0;
	}

	if (n - k < k) {
		k = n - k;
	}

	double s = 1; 
	int i;
	for (i = n - k + 1; i <= n; i++) {
		s *= i;
	}
	return s / factorial_d(k);
}
