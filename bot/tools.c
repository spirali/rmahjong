
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
