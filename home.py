from martian_lights.behaviors.rotary_brightness import rotary_brightness
from martian_lights.behaviors.time_based_scene_cycling import time_based_scene_cycling
from martian_lights.helpers.zll_switch import *

state_path = 'state.json'

def run(ml):
	bathroom = ml.namespace('bathroom')
	bathroom_group_id = 2
	rotary_brightness(
		bathroom.namespace('rot_bri'),
		rotary_sensor_id=14, # Lutron Aurora's rotary switch
		group_id=bathroom_group_id,
		display_name='Bathroom rotary',
		slow_rotation_turns_lights_to=None,
		fast_rotation_turns_lights_to=None,
	)

	time_based_scene_cycling(
		bathroom.namespace('scenes'),
		switch_sensor_id=15, # Lutron Aurora's big button,
		group_id=bathroom_group_id,
		on_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.SHORT_RELEASE),
		off_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.SHORT_RELEASE),
		cycle_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.LONG_RELEASE),
		scenes=[
			('T07:00:00/T12:00:00', 'wjg08c8U6YpmGgp'), # Energize
			('T12:00:00/T19:00:00', 'ZdoNb40lFPAs19y'), # Bright
			('T19:00:00/T22:00:00', '49N5awEOEXcEm73'), # Dimmed
			('T22:00:00/T07:00:00', 'tBFcir3B4akYah8'), # Nightlight
		],
	)
