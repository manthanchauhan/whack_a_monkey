"""
all functions which do not qualify as class methods
"""
import datetime

def Time():
	"""
	returns current time in seconds
	i.e) 3:15:43 --> 3 * 3600 + 15 * 60 + 43
	"""
	time = str(datetime.datetime.now())
	time = 3600 * int(time[11:13]) + 60 * int(time[14:16]) + int(time[17:19])
	return time