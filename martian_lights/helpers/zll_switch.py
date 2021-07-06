import enum

class ZLLSwitchButton(enum.Enum):
	TOP = 1
	DIM_UP = 2
	DIM_DOWN = 3
	BOTTOM = 4

class ZLLSwitchEventType(enum.Enum):
	INITIAL_PRESS = 0
	HOLD = 1
	SHORT_RELEASE = 2
	LONG_RELEASE = 3

def zll_switch_event(button, event_type):
	return f'{button.value}00{event_type.value}'
