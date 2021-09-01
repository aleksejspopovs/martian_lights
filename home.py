from martian_lights.behaviors.rotary_brightness import rotary_brightness
from martian_lights.behaviors.subset_cycling import subset_cycling
from martian_lights.behaviors.time_based_scene_cycling import time_based_scene_cycling
from martian_lights.behaviors.zll_switch_brightness import zll_switch_brightness
from martian_lights.helpers.schema import action_put, condition
from martian_lights.helpers.zll_switch import *

state_path = 'state.json'

def make_bathroom(ml):
	group_id = 2
	rotary_brightness(
		ml.namespace('rot_bri'),
		rotary_sensor_id=14, # Lutron Aurora's rotary switch
		group_id=group_id,
		display_name='Bathroom rotary',
		slow_rotation_turns_lights_to=None,
		fast_rotation_turns_lights_to=None,
	)

	time_based_scene_cycling(
		ml.namespace('scenes'),
		switch_sensor_ids=[15], # Lutron Aurora's big button,
		group_id=group_id,
		on_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.SHORT_RELEASE),
		off_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.SHORT_RELEASE),
		cycle_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.LONG_RELEASE),
		scenes=[
			('T07:00:00/T12:00:00', 'wjg08c8U6YpmGgp'), # Energize
			('T12:00:00/T19:00:00', 'ZdoNb40lFPAs19y'), # Bright
			('T19:00:00/T22:00:00', '49N5awEOEXcEm73'), # Dimmed
			('T22:00:00/T07:00:00', 'tBFcir3B4akYah8'), # Nightlight
		],
		display_name='Bathroom scenes',
	)


def make_living_room(ml):
	group_id = 3
	switch_ids = [42, 46] # couch, dining area

	scene_cycle_state_id = time_based_scene_cycling(
		ml.namespace('scenes'),
		switch_sensor_ids=switch_ids,
		group_id=group_id,
		on_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.INITIAL_PRESS),
		off_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.INITIAL_PRESS),
		cycle_event=zll_switch_event(ZLLSwitchButton.BOTTOM, ZLLSwitchEventType.LONG_RELEASE),
		scenes=[
			('T07:00:00/T12:00:00', '6VE4rvAva5a3YLd'), # Energize
			('T12:00:00/T19:00:00', 'n0AH1Tc85L8Rc-3'), # Bright
			('T19:00:00/T07:00:00', 'wVOwX6LGwOyQIiE'), # Dimmed
		],
		display_name='Living room scenes',
	)

	for switch_id in switch_ids:
		zll_switch_brightness(
			ml.namespace(f'bri_{switch_id}'),
			switch_sensor_id=switch_id,
			group_id=group_id,
			display_name='Living room brightness',
		)

	subset_cycling(
		ml.namespace('subset'),
		switch_sensor_ids=switch_ids,
		advance_event=zll_switch_event(ZLLSwitchButton.BOTTOM, ZLLSwitchEventType.SHORT_RELEASE),
		reset_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.INITIAL_PRESS),
		extra_on_conditions=[
			condition(f'/sensors/{scene_cycle_state_id}/state/status', 'gt', '1'),
		],
		group_id=group_id,
		subsets=[
			['1', '2', '3', '9', '10'],
			['1', '2', '3'],
			['9', '10'],
		],
		display_name='Living room subset',
	)


def make_bedroom(ml):
	group_id = 4
	switch_id = 2
	time_based_scene_cycling(
		ml.namespace('scenes'),
		switch_sensor_ids=[switch_id],
		group_id=group_id,
		on_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.INITIAL_PRESS),
		off_event=zll_switch_event(ZLLSwitchButton.BOTTOM, ZLLSwitchEventType.INITIAL_PRESS),
		cycle_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.INITIAL_PRESS),
		scenes=[
			('T07:00:00/T12:00:00', '4F0yl9YDbgf29Aa'), # Energize
			('T12:00:00/T19:00:00', '5wmuhH4G9GFJMyV'), # Relax
			('T19:00:00/T21:00:00', 'YKF5lteVdMkcfJN'), # Dimmed
			('T21:00:00/T07:00:00', 'rT8HfqWAYtT50U5'), # Nightlight
		],
		display_name='Bedroom scenes',
	)

	zll_switch_brightness(
		ml.namespace('bri'),
		switch_sensor_id=switch_id,
		group_id=group_id,
		display_name='Bedroom brightness',
	)


def make_office(ml):
	group_id = 1
	switch_id = 6

	scene_cycle_state_id = time_based_scene_cycling(
		ml.namespace('scenes'),
		switch_sensor_ids=[switch_id],
		group_id=group_id,
		on_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.INITIAL_PRESS),
		off_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.INITIAL_PRESS),
		cycle_event=zll_switch_event(ZLLSwitchButton.BOTTOM, ZLLSwitchEventType.LONG_RELEASE),
		scenes=[
			('T07:00:00/T10:00:00', 'aBmkEihL80mswg5'), # Energize
			('T10:00:00/T17:00:00', '1zpkcVBUVnUMTmi'), # Concentrate
			('T17:00:00/T20:00:00', 'GhRn89mSmwR2f-m'), # Read
			('T20:00:00/T23:00:00', 'c90XW-mrnIhJ9z-'), # Relax
			('T23:00:00/T07:00:00', 'RL747XrAtHPQvPh'), # Nightlight
		],
		display_name='Office scenes',
	)

	zll_switch_brightness(
		ml.namespace(f'bri'),
		switch_sensor_id=switch_id,
		group_id=group_id,
		display_name='Office brightness',
	)

	subset_cycling(
		ml.namespace('subset'),
		switch_sensor_ids=[switch_id],
		advance_event=zll_switch_event(ZLLSwitchButton.BOTTOM, ZLLSwitchEventType.SHORT_RELEASE),
		reset_event=zll_switch_event(ZLLSwitchButton.TOP, ZLLSwitchEventType.INITIAL_PRESS),
		extra_on_conditions=[
			condition(f'/sensors/{scene_cycle_state_id}/state/status', 'gt', '1'),
		],
		group_id=group_id,
		subsets=[
			['4', '5', '6', '11'],
			['4', '5', '6'],
			['11'],
		],
		display_name='Office subset',
	)


def run(ml):
	make_bathroom(ml.namespace('bathroom'))
	make_living_room(ml.namespace('living_room'))
	make_bedroom(ml.namespace('bedroom'))
	make_office(ml.namespace('office'))
