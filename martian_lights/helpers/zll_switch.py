import enum

from martian_lights.helpers.schema import condition

class ZLLSwitchButtonType(enum.Enum):
	TOP = 1
	DIM_UP = 2
	DIM_DOWN = 3
	BOTTOM = 4
	ONE = 1
	TWO = 2
	THREE = 3
	FOUR = 4

class ZLLSwitchEventType(enum.Enum):
	INITIAL_PRESS = 0
	HOLD = 1
	SHORT_RELEASE = 2
	LONG_RELEASE = 3

def zll_switch_event(button, event_type):
	return f'{button.value}00{event_type.value}'

class ZLLSwitchButton:
	def __init__(self, sensor_id, button_type):
		self.sensor_id = sensor_id
		self.button_type = button_type

	def conditions(self, event_type):
		return [
			condition(f'/sensors/{switch_sensor_id}/state/lastupdated', 'dx'),
			condition(
				f'/sensors/{self.sensor_id}/state/buttonevent',
				'eq',
				zll_switch_event(self.button_type, self.event_type)
			),
		]

	def initial_press(self):
		return self.conditions(ZLLSwitchEventType.INITIAL_PRESS)

	def hold(self):
		return self.conditions(ZLLSwitchEventType.HOLD)

	def short_release(self):
		return self.conditions(ZLLSwitchEventType.SHORT_RELEASE)

	def long_release(self):
		return self.conditions(ZLLSwitchEventType.LONG_RELEASE)

class ZLLSwitch:
	def __init__(self, sensor_id):
		self.sensor_id = sensor_id

	def button(self, button_type):
		return ZLLSwitchButton(self.sensor_id, button_type)

	def top(self):
		return self.button(ZLLSwitchButtonType.TOP)

	def dim_up(self):
		return self.button(ZLLSwitchButtonType.DIM_UP)

	def dim_down(self):
		return self.button(ZLLSwitchButtonType.DIM_DOWN)

	def bottom(self):
		return self.button(ZLLSwitchButtonType.BOTTOM)

	def one(self):
		return self.button(ZLLSwitchButtonType.ONE)

	def two(self):
		return self.button(ZLLSwitchButtonType.TWO)

	def three(self):
		return self.button(ZLLSwitchButtonType.THREE)

	def four(self):
		return self.button(ZLLSwitchButtonType.FOUR)
