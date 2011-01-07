# MIT License
# 
# Copyright (c) 2011 Adam Preble
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import procgame.game

class PrepareToStart(procgame.game.Mode):
	"""Manages waiting for the game to be ready to start."""
	def __init__(self, game):
		super(PrepareToStart, self).__init__(game=game, priority=9)
	
	def mode_started(self):
		self.game.trough.changed_handlers.append(self.trough_changed)
		self.pulse_and_delay()
	
	def mode_stopped(self):
		self.game.trough.changed_handlers.remove(self.trough_changed)
	
	def trough_changed(self):
		self.check_ready()
	
	def check_ready(self):
		"""Perform checks on the system state to see if we are ready to start the game."""
		if self.game.trough.is_full():
			self.ready()
			return True
		
		return False
	
	def pulse_and_delay(self):
		ready = self.check_ready()
		if not ready:
			self.game.coils.upperRightPopper.pulse()
			self.game.coils.lowerRightPopper.pulse()
			self.delay(name='pulse_and_delay',
			           event_type=None,
			           delay=5.0,
			           handler=self.pulse_and_delay)
		
	def ready(self):
		"""Called to indicate that the game is ready to start."""
		# Remove attract mode from mode queue - Necessary?
		self.game.modes.remove(self)
		# Initialize game	
		self.game.start_game()
		# Add the first player
		self.game.add_player()
		# Start the ball.  This includes ejecting a ball from the trough.
		self.game.start_ball()



class Attract(procgame.game.Mode):
	"""A mode that runs whenever the game is in progress."""
	def __init__(self, game):
		super(Attract, self).__init__(game=game, priority=9)
		# TODO: Setup an attract mode layer
	
	def mode_started(self):
		self.game.lamps.startButton.schedule(schedule=0xffff0000, cycle_seconds=0, now=False)
		self.game.lamps.insertPlayfieldLower.enable()
		self.game.lamps.insertPlayfieldMiddle.enable()
		self.game.lamps.insertPlayfieldUpper.enable()
	
	def mode_stopped(self):
		self.game.lamps.startButton.disable()

	def sw_startButton_active(self, sw):
		self.game.modes.remove(self)
		# TODO: PrepareToStart should just be 'startup ball search.'
		#       We don't want to start the game immediately after we find the balls.
		self.game.modes.add(PrepareToStart(game=self.game))
