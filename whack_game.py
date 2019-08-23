"""
Author: Manthan Chauhan
Dated: 10-3-19
----------------------------
class definition of WhackGame

The program is a state machine with details as follows:
[Idle state] --> [Start state] --> [end state]

Idle state: the game is just displaying Monkey face at random positions, initially game starts in idle
			state.
Start state: the game is displaying Monkey at random positions and monitoring whether the player has
			hit the monkey in the provided time before the Monkey vanishes, this state arrives as soon
			as the operator presses "Ctrl+C"
End state: The game displays an ending message along with the score and ends. This state arrives as
			soon as the player misses a Monkey.
"""

import cv2 
import json
import numpy as np
from collections import namedtuple
import datetime
import random
import time
import sys
import cv2.aruco as aruco

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from my_funcs import Time

Marker = namedtuple('Marker', 'id_ origin rvec tvec')
Monkey = namedtuple('Monkey', 'id_ obj stay_time if_caught arrive_time')
ScoreBoard = namedtuple('ScoreBoard', 'score penalty flew')
# just have a look at what "namedtuple" is, and you'll get it.


class WhackGame:
	# An instance of this class represents a session of the game

	def __init__(self, ids, camera):
		# this fuction initializes openGL and openCV stuff.

		# the file "config.json" stores all required configuration in .json format. Have a look at that file.
		with open('config.json', 'r') as file:
			self._config = json.load(file)
			# the above method loads the contents of "config.json" file in `config._paths` in `dict()` format.
			# This was done so that now you can edit all project configuration at one place, making lives easier.
		
		self._ids = ids
		self._camera = cv2.VideoCapture(camera)

		self._marker_size = self._config['marker_size']	# 1 openGL unit = marker_size (kind of a scale to place 3D models)
		self._marker_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_250)

		# here follows camera calibration stuff
		self._cam_matrix = None
		self._dist_matrix = None
		self._init_camera()		# makes camera able to identify depths and, can skip
		
		# initializes openGL for rendering models, do skip this one
		self._init_opengl()		
		
		self._state = None 		# state of the game
		self._monkey = None
		self._score_board = None	# score of current player

		self._visible_ids = None
		self._record = None

		self._last_penalty = None
		self._kill = False
		# now continue reading `main.py` and you'll come back here later
		return
		# self._bg_texture = None		# this is for 3D model rendering
		# self._import_models()

	def _init_camera(self):
		"""
		it loads distortion matrix and rotation matrix of camera to understand the 3D world
		ignore this one
		"""
		with np.load(self._config['camera_npz']) as npz_file:
			self._cam_matrix, self._dist_matrix, _, _ = [npz_file[i] for i in ('mtx', 'dist', 'rvecs', 'tvecs')]

		# its a good programming ethic to return explicitly
		return

	def _init_opengl(self):
		# Initializes openGL stuff, ignore this one as well
		glutInit()
		glutInitWindowSize(640, 480)
		glutInitWindowPosition(625, 100)
		glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
		glutCreateWindow("Whack-A-Monkey")
		glClearColor(0, 0, 0, 0)
		glClearDepth(1)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_COLOR_MATERIAL)
		glShadeModel(GL_SMOOTH)
		glMatrixMode(GL_MODELVIEW)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		
		self._bg_texture = glGenTextures(1)
		
		glutDisplayFunc(self._draw_gl_scene)
		glutIdleFunc(self._draw_gl_scene)
		glutReshapeFunc(self._resize_gl)

		return 

	def _draw_gl_scene(self):
		# displays frames one by one

		"""
		the `try-except-finally` block is used to catch the `KeyboardInterrupt` (Ctrl + C).
		`KeyboardInterrupt` causes the game to shift from 'idle' state to 'start' state
		The operator of the game provides this `KeyboardInterrupt` whenever the player is ready to play
		"""
		try:
			# again some openGL stuff to ignore
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

			# capture an image from camera
			ret, image = self._camera.read()
			assert ret, 'image not captured properly'

			"""
			first we draw the captured image as background of openGL window,
			then we draw AR models with certain translation and rotation over the background to create an AR effect
			"""

			# draw background image
			self._draw_bg(image)

			# obtain a list of visible AR markers
			ar_list = self._detect_markers(image)

			if self._state is 'idle':
				# visible_ids = [marker.id_ for marker in ar_list]
				# print(f'ids: {visible_ids}')

				# do nothing in idle state
				pass

			elif self._state is 'start' and not self._monkey.if_caught:
				"""
				if game is in start state and the player haven't caught the current monkey yet,
				check if the monkey was caught in the current frame.
				"""
				visible_ids = [marker.id_ for marker in ar_list]

				# print('-----------------------------------------')
				# print(f'previous ids : {self._visible_ids}')
				# print(f'current ids: {visible_ids}')

				absentees = self._find_absentees(visible_ids, self._config['past'])

				self._visible_ids = visible_ids.copy()
				
				# print(f'absentees = {absentees}')
				# print(f'monkey id: {self._monkey.id_}')
				# print(f'monkey id : {self._monkey.id_}')

				for id_ in absentees:
					# print(f'testing id {id_}')
					if id_ != self._monkey.id_:
						"""
						if any non-monkey id is not visible it means that player caught the wrong id,
						in this condition the score is reduced by `penalty`
						"""
						# print(f'id {id_} is not visible')
						# time.sleep(3)
							
						score, penalty, flew = self._score_board
						self._score_board = ScoreBoard(score, penalty + 1, flew)
						print(self._score_board.penalty)

					else:
						"""
						if monkey id is not visible that means the player caugth the monkey in the current frame
						score is increased by `award` and flag is raised so that same monkey isn't caught in next frame
						"""
						score, penalty, flew = self._score_board
						self._score_board = ScoreBoard(score + 1, penalty, flew)
						# print('you got it!!')

						id_, obj, stay, caught, arrive = self._monkey
						self._monkey = Monkey(id_, obj, stay, True, arrive)

				print('-----------------------------------------')

			elif self._state == 'start' and self._monkey.if_caught:
				# current monkey has been already caught, wait for new monkey to appear
				pass

			# render monkey as per `self._monkey_id`
			self._render_models(ar_list)

			# openGL stuff to ignore
			glutSwapBuffers()

		except KeyboardInterrupt:
			if self._state == 'idle':
				# if `KeyboardInterrupt` was caught in idle state, move to start state
				self._state = 'start'
				
				# ScoreBoard = namedtuple('ScoreBoard', 'score penalty flew')
				self._score_board = ScoreBoard(0, 0, 0)
				
				# Monkey = namedtuple('Monkey', 'id_ obj stay_time if_caught arrive_time')

				self._visible_ids = list(self._ids) 	# all ids are initailly visible

				print('starting session in 5s')
				time.sleep(5)
				print('play!!')
				
				self._record = []

				self._monkey = Monkey(random.choice(self._ids), 
					self._monkey.obj,
					self._monkey.stay_time,
					False,
					Time()
					)

			else:	
				self._kill = True

		finally:
			# change monkey id if certain time has passed
			self._change_monkey_id()
			
			return

	def _find_absentees(self, visible_ids, past):
		binary_seq = [(id_ in visible_ids) for id_ in self._ids]
		# print(f'binary_seq: {binary_seq}')
		self._record.append(binary_seq)

		if len(self._record) < past // 2:
			return []

		length = min(past, len(self._record))

		absentees = [False for id_ in self._ids]

		# print(f'length = {length}')
		for i in range(0, len(self._ids)):
			for j in range(0, length):
				absentees[i] = absentees[i] or self._record[::-1][j][i]


		ans = [self._ids[id_] for id_ in range(0, len(absentees)) if not absentees[id_]]

		if len(self._record) > past:
			self._record = self._record[-10:]

		return ans


	def _render_models(self, ar_list):
		for marker in ar_list:
			if marker.id_ == self._monkey.id_:
				
				self._set_overlay_matrix(marker)
				glutSolidCube(1)
				return

	def _set_overlay_matrix(self, marker):
		center, rvec, tvec = marker.origin, marker.rvec, marker.tvec

		f = 1000
		n = 1
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		alpha = self._cam_matrix[0][0]
		beta = self._cam_matrix[1][1]
		cx = self._cam_matrix[0][2]
		cy = self._cam_matrix[1][2]

		m1 = np.array([
			[alpha / cx, 0, 0, 0],
			[0, beta / cy, 0, 0],
			[0, 0, -(f + n) / (f - n), (-2.0 * f * n) / (f - n)],
			[0, 0, -1, 0],
			])

		glLoadMatrixd(m1.T)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		
		tvec[0], tvec[1], tvec[2] = tvec[0], -tvec[1], -tvec[2]
		rvec[1], rvec[2] = -rvec[1], -rvec[2]

		rotation_matrix = cv2.Rodrigues(rvec)[0]
		v = np.c_[rotation_matrix, tvec.T]
		m = np.r_[v, np.array([[0, 0, 0, 1]])]

		glLoadMatrixd(m.T)
		glTranslatef(0, 0, 0)


	def _detect_markers(self, image):
		"""
		returns a list of `Marker` objects containing info of all visible markers.
		you can ignore this one as well
		"""

		# we create an empty list and add info of all visible markers in it.
		aruco_list = []
		image_copy = image

		# ArUco detection is better in B/W images
		image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		corners, ids, _ = aruco.detectMarkers(image,
			self._marker_dict,
			self._cam_matrix,
			self._dist_matrix
			)

		aruco.drawDetectedMarkers(image_copy, corners, ids)
		cv2.imshow('openCV', image_copy)
		cv2.waitKey(1)

		if ids is None:
			# print('no id is detected')
			return []

		for i in range(0, len(ids)):
			rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners,
				self._marker_size,
				self._cam_matrix,
				self._dist_matrix
				)

			origin = np.float32([[0, 0, 0]])
			origin, jac = cv2.projectPoints(origin,
				rvec[i],
				tvec[i],
				self._cam_matrix,
				self._dist_matrix
				)

			id_, origin, rvec, tvec = ids[i][0], tuple(origin[0][0].ravel()), rvec[i][0], tvec[i][0]
			marker = Marker(id_, origin, rvec, tvec)
			aruco_list.append(marker)

		aruco_list = tuple(aruco_list)
		assert len(aruco_list) != 0, f'empty `aruco_list`'

		return aruco_list

	@staticmethod
	def _draw_bg(image):
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		height, width = image.shape[:2]

		# placing image as texture in background plane
		glDisable(GL_DEPTH_TEST)
		glDisable(GL_LIGHTING)
		glDisable(GL_LIGHT0)
		glEnable(GL_TEXTURE_2D)

		texture_id = glGenTextures(1)

		glBindTexture(GL_TEXTURE_2D, texture_id)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glColor3f(1, 1, 1)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		glBegin(GL_QUADS)
		glTexCoord2d(0, 1)
		glVertex3d(-1, -1, 0)
		glTexCoord2d(1, 1)
		glVertex3d(1, -1, 0)
		glTexCoord2d(1, 0)
		glVertex3d(1, 1, 0)
		glTexCoord2d(0, 0)
		glVertex3d(-1, 1, 0)
		glEnd()

		glMatrixMode(GL_PROJECTION)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glDisable(GL_TEXTURE_2D)

		return None



	@staticmethod
	def _resize_gl(width, height):
		ratio = width/height
		glMatrixMode(GL_PROJECTION)
		glViewport(0, 0, width, height)
		gluPerspective(45, ratio, 0.1, 1000)

	def _import_models(self):
		pass

	def open_game(self):
		# this functions handles the scene before the player starts playing
		pass

	def test_setup(self):
		# tests if all ids are clearly visible

		"""
		captures an image
		if image is not captured due to any system error, ret is False, else, ret is True.
		"""
		ret, image = self._camera.read()
		assert ret, 'image not captured properly'

		ret, image2 = self._camera.read()
		assert ret, 'image not captured properly'


		# detects all ArUco makers and returns a list of `Marker` objects
		# Marker = namedtuple('Marker', 'id_ origin rvec tvec')
		ar_list = self._detect_markers(image)
		ar_list2 = self._detect_markers(image2)

		# create a list of visible ArUco marker ids
		# read about "list comprehensions"
		visible_ids = [marker.id_ for marker in ar_list]
		visible_ids2 = [marker.id_ for marker in ar_list2]


		# check if all ids are visible
		for id_ in self._ids:
			if id_ not in visible_ids and id_ not in visible_ids2:
				cv2.imshow("setup failed", image)
				cv2.waitKey(0)
				raise Exception(f'id {id_} is not found')

		return

	def _change_monkey_id(self):
		if self._kill:
			print(f'Sorry! but the game encountered some error please wait for a few seconds')
			sys.exit()

		now_time = Time()

		# find time spanned since the current monkey appeared
		time_spanned = now_time - self._monkey.arrive_time 
		
		if time_spanned >= self._config['monkey_visible']:
			# if its time to generate the new monkey
			
			if self._state is 'start' and not self._monkey.if_caught:
				# if monkey was not caught in time, player looses
				# print(f'Oops! this monkey ran away at {now_time} flew = {self._score_board.flew}')

				self._score_board = ScoreBoard(self._score_board.score, 
					self._score_board.penalty, 
					self._score_board.flew + 1
					)

				if self._score_board.score == self._config['level2'] or self._score_board.score == self._config['level3']:
					self._config['monkey_visible'] /= 2

				if self._score_board.flew > self._config['chances']:
					self._state = 'end'
					self._show_scores()

					sys.exit()

			new_id = random.choice(self._ids)

			while new_id == self._monkey.id_:
				new_id = random.choice(self._ids)
	
			_, obj, stay, _, _ = self._monkey
			self._monkey = Monkey(new_id, obj, stay, False, Time())

			self._visible_ids = list(self._ids)
			print(f'changed monkey id to {self._monkey.id_} at time {self._monkey.arrive_time}')

	def _show_scores(self):
		score, penalty, _ = self._score_board

		print('*********************************')
		print(f'* Monkeys caught:\t{score}\t*')
		print(f'* Penalties:\t\t{penalty * self._config["penalty_strength"]}\t*')
		print('*********************************')
		print(f'time: {self._config["monkey_visible"]}')


	def start_game(self):
		self._state = 'idle'

		# select a random ArUco id to display monkey
		monkey_id = random.choice(self._ids)

		# modify `self._monkey` will new id but same Ar object(.obj)
		# Monkey = namedtuple('Monkey', 'id_ obj stay_time if_caught arrive_time')
		monkey_obj = None

		self._monkey = Monkey(random.choice(self._ids),
			monkey_obj,
			self._config['monkey_visible'],
			False,
			Time()
			)
		# print(self._monkey.id_)

		"""
		start rendering AR models
		`glutMainLoop()` calls `_draw_gl_scene` infinitely
		"""
		glutMainLoop()
		return 