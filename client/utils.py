
def left_shift_list(lst, count = 1):
	return lst[count:] + lst[:count]

def right_shift_list(lst, count = 1):
	return lst[-count:] + lst[:-count]

