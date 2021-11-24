from martian_lights.behaviors.rotary_brightness import rotary_brightness
from martian_lights.behaviors.time_based_scene_cycling import time_based_scene_cycling
from martian_lights.behaviors.two_subgroup_cycling import two_subgroup_cycling
from martian_lights.behaviors.zll_switch_brightness import zll_switch_brightness
from martian_lights.helpers.schema import action_put, condition
from martian_lights.helpers.zll_switch import *

state_path = 'state.json'

def make_bathroom(ml):
	group_id = 2
	rotary_brightness(
		ml.namespace('rot_bri'),
		rotary_sensor_id=14, # Lutron Aurora's rotary dial
		group_id=group_id,
		display_name='Bathroom dial',
		slow_rotation_turns_lights_to=None,
		fast_rotation_turns_lights_to=None,
	)

	switch = ZLLSwitch(15) # the top button on the Aurora
	time_based_scene_cycling(
		ml.namespace('scenes'),
		group_id=group_id,
		on_conditions=[switch.top().short_release()],
		off_conditions=[switch.top().short_release()],
		cycle_conditions=[switch.top().long_release()],
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
	switches = [
		ZLLSwitch(42), # couch
		ZLLSwitch(46), # dining area
	]

	scene_cycle_state_id = time_based_scene_cycling(
		ml.namespace('scenes'),
		group_id=group_id,
		on_conditions=[s.top().initial_press() for s in switches],
		off_conditions=[s.top().initial_press() for s in switches],
		cycle_conditions=[s.bottom().long_release() for s in switches],
		scenes=[
			('T07:00:00/T12:00:00', '6VE4rvAva5a3YLd'), # Energize
			('T12:00:00/T19:00:00', 'n0AH1Tc85L8Rc-3'), # Bright
			('T19:00:00/T07:00:00', 'wVOwX6LGwOyQIiE'), # Dimmed
		],
		display_name='Living room scenes',
	)

	for switch in switches:
		zll_switch_brightness(
			ml.namespace(f'bri_{switch.sensor_id}'),
			switch=switch,
			group_id=group_id,
			display_name='Living room brightness',
		)

	two_subgroup_cycling(
		ml.namespace('subgroup'),
		# these groups already exist
		subgroups=[
			6, # LR Dining
			5, # LR Couch
		],
		advance_conditions=[s.bottom().short_release() for s in switches],
	)


def make_bedroom(ml):
	group_id = 4
	wall_switch = ZLLSwitch(2)
	
	puck_id_rotary = 53
	puck_button = ZLLSwitch(54)
	
	time_based_scene_cycling(
		ml.namespace('scenes'),
		group_id=group_id,
		on_conditions=[wall_switch.top().initial_press(), puck_button.top().initial_press()],
		off_conditions=[wall_switch.bottom().initial_press(), puck_button.top().initial_press()],
		cycle_conditions=[wall_switch.top().initial_press(), puck_button.top().long_release()],
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
		switch=wall_switch,
		group_id=group_id,
		display_name='Bedroom brightness',
	)

	rotary_brightness(
		ml.namespace('rot_bri'),
		rotary_sensor_id=puck_id_rotary,
		group_id=group_id,
		display_name='Bedroom dial',
		slow_rotation_turns_lights_to=None,
		fast_rotation_turns_lights_to=None,
	)


def make_office(ml):
	group_id = 1
	switch = ZLLSwitch(6)

	scene_cycle_state_id = time_based_scene_cycling(
		ml.namespace('scenes'),
		group_id=group_id,
		on_conditions=[switch.top().initial_press()],
		off_conditions=[switch.top().initial_press()],
		cycle_conditions=[switch.bottom().long_release()],
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
		switch=switch,
		group_id=group_id,
		display_name='Office brightness',
	)

	# these groups are created with type: LightGroup, so they do not appear on
	# the mobile app
	overhead_group = ml.resource(
		'groups',
		'overhead_group',
		{'name': 'OF Overhead', 'lights': ['4', '5', '6']},
	)
	table_lamp_group = ml.resource(
		'groups',
		'table_lamp_group',
		{'name': 'OF Table', 'lights': ['11']},
	)

	two_subgroup_cycling(
		ml.namespace('subgroup'),
		subgroups=[overhead_group, table_lamp_group],
		advance_conditions=[switch.bottom().short_release()],
	)


def run(ml):
	make_bathroom(ml.namespace('bathroom'))
	make_living_room(ml.namespace('living_room'))
	make_bedroom(ml.namespace('bedroom'))
	make_office(ml.namespace('office'))
