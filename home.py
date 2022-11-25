from martian_lights.behaviors.group_toggle import group_toggle
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
		toggle_conditions=[switch.top().short_release()],
		cycle_conditions=[switch.top().long_release()],
		scenes=[
			('T07:00:00/T12:00:00', '6vIegaD7zCterRy'), # Energize
			('T12:00:00/T19:00:00', 'fMvcJgY4Vv0NaGu'), # Bright
			('T19:00:00/T22:00:00', 'OA80foEuTaVeVcq'), # Dimmed
			('T22:00:00/T07:00:00', '10Xnn5pUoEC34dv'), # Nightlight
		],
		display_name='Bathroom scenes',
	)


def make_living_room(ml):
	tap_switches = [ZLLSwitch(57), ZLLSwitch(63)]
	rotaries = [56, 62]
	couch_switch = ZLLSwitch(46)

	foh_group_id = 7 # front of house
	schedule = [
		('T07:00:00/T12:00:00', 'iJR082ijBR0ejKA'), # Energize
		('T12:00:00/T19:00:00', 'UiMXRDvpXuAtd7e'), # Bright
		('T19:00:00/T07:00:00', 'lf19gLwaFlFz02D'), # Dimmed
	]

	time_based_scene_cycling(
		ml.namespace(f'scenes'),
		group_id=foh_group_id,
		on_conditions=[s.one().short_release() for s in tap_switches],
		off_conditions=[s.three().short_release() for s in tap_switches],
		toggle_conditions=[couch_switch.top().short_release()],
		cycle_conditions=[s.two().short_release() for s in tap_switches],
		scenes=schedule,
		display_name='Living room scenes',
	)

	for rotary in rotaries:
		rotary_brightness(
			ml.namespace(f'bri_{rotary}'),
			rotary_sensor_id=rotary,
			group_id=foh_group_id,
			display_name='Living room brightness',
			slow_rotation_turns_lights_to=None,
			fast_rotation_turns_lights_to=None,
		)

	subgroups = [
		(10, ZLLSwitchButtonType.ONE, ['aLvpEr9eDDkP47b', 'LmVi205gkh9aG4f', '83IINrA9VED9SUd']), # hallway
		(3, ZLLSwitchButtonType.TWO, ['6VE4rvAva5a3YLd', 'n0AH1Tc85L8Rc-3', 'wVOwX6LGwOyQIiE']), # living room
		(9, ZLLSwitchButtonType.THREE, ['0Ind8LjEEyjcxaM', 'Ni2aDscg7GICwjj', 'B-JjJkUEuKiZboy']), # kitchen
		(6, ZLLSwitchButtonType.FOUR, ['0p3DAJiqlukpdbL', 'P3ATIR7FnoRD71p', 'gVhhGq4JbKbBNcN']), # alcove
	]

	for subgroup_id, button_type, _ in subgroups:
		group_toggle(
			ml.namespace(f'toggle_{subgroup_id}'),
			group_id=subgroup_id,
			conditions=[s.button(button_type).long_release() for s in tap_switches],
		)

	# couch switch
	lr_group_id = 3

	zll_switch_brightness(
		ml.namespace(f'bri_couch'),
		switch=couch_switch,
		group_id=lr_group_id,
		display_name='Couch brightness',
	)

	group_toggle(
		ml.namespace('toggle_couch'),
		group_id=lr_group_id,
		conditions=[couch_switch.bottom().short_release()],
	)


def make_bedroom(ml, scenes):
	group_id = 4
	wall_switch = ZLLSwitch(2)
	
	puck_id_rotary = 67
	puck_button = ZLLSwitch(68)
	
	time_based_scene_cycling(
		ml.namespace('scenes'),
		group_id=group_id,
		on_conditions=[wall_switch.top().initial_press()],
		off_conditions=[wall_switch.bottom().initial_press()],
		toggle_conditions=[puck_button.top().initial_press()],
		cycle_conditions=[wall_switch.top().initial_press(), puck_button.top().long_release()],
		scenes=[
			('T07:00:00/T12:00:00', scenes[group_id]['Energize']),
			('T12:00:00/T19:00:00', scenes[group_id]['Relax']),
			('T19:00:00/T21:00:00', scenes[group_id]['Dimmed']),
			('T21:00:00/T07:00:00', scenes[group_id]['Nightlight']),
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
	wall_switch = ZLLSwitch(6)
	desk_switch = ZLLSwitch(42)
	switches = [wall_switch, desk_switch]

	scene_cycle_state_id = time_based_scene_cycling(
		ml.namespace('scenes'),
		group_id=group_id,
		toggle_conditions=[s.top().initial_press() for s in switches],
		cycle_conditions=[s.bottom().long_release() for s in switches],
		scenes=[
			('T07:00:00/T10:00:00', 'NppUTl2AYdRNLQF'), # Energize
			('T10:00:00/T17:00:00', '4hNMi8DCp2MBYJN'), # Concentrate
			('T17:00:00/T20:00:00', 'LZvd86NAkzlbhEN'), # Read
			('T20:00:00/T23:00:00', 'lZadNORbla8JrLy'), # Relax
			('T23:00:00/T07:00:00', '2Ne8xZRiXKl00FK'), # Nightlight
		],
		display_name='Office scenes',
	)

	for i, switch in enumerate(switches):
		zll_switch_brightness(
			ml.namespace(f'bri_{i}'),
			switch=switch,
			group_id=group_id,
			display_name='Office brightness',
		)

	# these groups are created with type: LightGroup, so they do not appear on
	# the mobile app
	overhead_group = ml.resource(
		'groups',
		'overhead_group',
		{'name': 'OF Overhead', 'lights': ['29', '30', '31']},
	)
	desk_lamp_group = ml.resource(
		'groups',
		'desk_lamp_group',
		{'name': 'OF Desk', 'lights': ['10']},
	)

	two_subgroup_cycling(
		ml.namespace('subgroup'),
		subgroups=[overhead_group, desk_lamp_group],
		advance_conditions=[s.bottom().short_release() for s in switches],
	)


def run(ml):
	scenes = ml.read_resource('scenes', None)
	scenes_by_group = {}
	for scene_id, scene in scenes.items():
		group = int(scene['group'])
		if group not in scenes_by_group:
			scenes_by_group[group] = {}
		scenes_by_group[group][scene['name']] = scene_id

	make_bathroom(ml.namespace('bathroom'))
	make_living_room(ml.namespace('living_room'))
	make_bedroom(ml.namespace('bedroom'), scenes_by_group)
	make_office(ml.namespace('office'))
	pass
