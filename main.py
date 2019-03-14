"""
Author: Manthan Chauhan
Dated: 10-3-19
"""

# imports the class WhackGame from whack_game.py
from whack_game import WhackGame

if __name__=='__main__': # ignore, or do some Googling
	# following contents represents the main function

	# I assume you read about openCV on the link shared in group.
	# ArUco ids to display various AR objects,  
	ids = (1, 6, 3, 4)

	# 0 to use inbuilt webcam, 1 to use USB camera
	camera = 2

	# interesting part, creating a WhackGame object
	session = WhackGame(ids, camera)	
	# See whack_game.py before you proceed

	"""
	test if all ids and camera as set up properly,
	if not, an exception is raised
	read `WhackGame.test_setup()`
	"""
	session.test_setup()

	# start the game
	session.start_game()