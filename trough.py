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


class Trough(procgame.game.Mode):
	"""docstring for Trough"""
	
	trough_switch_names = ['leftTrough', 'centerTrough', 'rightTrough']
	
	changed_handlers = None
	
	ball_count = 0
	
	def __init__(self, game):
		super(Trough, self).__init__(game=game, priority=2)
		self.changed_handlers = []
		for name in self.trough_switch_names:
			for event_type in ['open', 'closed']:
				self.add_switch_handler(name=name, event_type=event_type, delay=None, handler=self._trough_switch_changed)
	
	def mode_started(self):
		self._update_ball_count()
		if self.game.switches.outhole.is_active():
			self.game.coils.outhole.pulse()
	
	def is_full(self):
		return self.ball_count == self.game.num_balls_total
	
	def _update_ball_count(self):
		count = self._count_balls()
		if count != self.ball_count:
			self.ball_count = count
			self.game.log('Trough now has %d balls.' % (self.ball_count))
			# [:] makes a copy of the array so it cannot be changed while we are looking at it
			for handler in self.changed_handlers[:]:
				handler()
	
	def _count_balls(self):
		count = 0
		for name in self.trough_switch_names:
			if self.game.switches[name].is_active():
				count += 1
		return count
	
	def _trough_switch_changed(self, sw):
		# Set a delay so we know that the trough state has settled.
		timer_name = 'trough_switch_change_timer'
		self.cancel_delayed(name=timer_name)
		self.delay(name=timer_name,
		           event_type=None,
		           delay=0.2,
		           handler=self._trough_switch_change_timer_expired)
	
	def _trough_switch_change_timer_expired(self):
		self._update_ball_count()
	
	def sw_outhole_active_for_100ms(self, sw):
		# TODO: Check that the outhole switch goes inactive momentarily, else pulse again.
		self.game.coils.outhole.pulse()
	
