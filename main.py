"""
Author: Manthan Chauhan
Dated: 10-3-19
"""
from whack_game import WhackGame

if __name__ == '__main__':
	# ArUco ids to display various AR objects,
	ids = (6, 8)

	camera = 0
	session = WhackGame(ids, camera)

	"""
	test if all ids and camera as set up properly,
	if not, an exception is raised
	read `WhackGame.test_setup()`
	"""
	session.test_setup()

	# start the game
	session.start_game()
